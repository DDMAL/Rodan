# Rodan on Kubernetes (k3s)

Plain-YAML manifests to run the Rodan stack on a k3s cluster (target: Arbutus). This is a
**lift-and-shift** of the existing Docker Swarm stack — same published images (`v3.3.1`, plus
`nightly` for iipsrv/rodan-client), reorganized as k8s workloads.

See the full design in `../.claude/plans/the-architecture-that-i-parallel-lampson.md`.

## Topology

- All services run on the k3s cluster. **Only `gpu-celery`** runs on a dedicated GPU node.
- Storage is **NFS on Arbutus**: `resources` (`/rodan/data`, ~883 GB, RWX), `pg_data` (PG 9.6
  PGDATA, RWO, `hard`), `pg_backup` (RWX). Static PV+PVC pairs, `Retain` reclaim.
- **Postgres runs in-cluster** (StatefulSet) on its NFS PGDATA.
- Entry point is **Traefik Ingress** for `rodan2.simssa.ca`, HTTP only — **TLS is terminated on
  an external edge server** that forwards plain HTTP. The kept `nginx` container does all internal
  routing.
- k8s Service names intentionally match the old Docker DNS names (`postgres`, `redis`, `rabbitmq`,
  `rodan-main`, `rodan-client`, `iipsrv`) because they're hardcoded in `rodan.conf` / `wait-for-app`.

## Files (apply in numeric order)

| File | Purpose |
|---|---|
| `00-namespace.yaml` | namespace `rodan` |
| `01-configmap.yaml` | `rodan-config` (non-secret env) |
| `02-secret.template.yaml` | template → copy to `02-secret.yaml`, fill in, apply (gitignored) |
| `10..15-*` | NFS PVs + PVCs (resources, pg_data, pg_backup) |
| `20-postgres.yaml` | Postgres StatefulSet + Service |
| `21-redis.yaml` / `22-rabbitmq.yaml` | broker/cache Deployments + Services |
| `30-rodan-main.yaml` | Django API Deployment + Service |
| `31/32/33-*celery.yaml` | celery / py3-celery / gpu-celery workers |
| `40-iipsrv.yaml` / `41-rodan-client.yaml` | image server + static client |
| `50-nginx.yaml` | reverse proxy Deployment + ClusterIP Service |
| `51-ingress.yaml` | Traefik Ingress (`rodan2.simssa.ca`) |
| `60-nvidia-device-plugin.yaml` | advertises `nvidia.com/gpu` on the GPU node |

## Before you apply — fill in placeholders

1. **NFS server IP** — replace `__ARBUTUS_NFS_IP__` in the three PV files:
   ```sh
   sed -i 's/__ARBUTUS_NFS_IP__/<real-nfs-ip>/' 10-pv-resources.yaml 12-pv-pgdata.yaml 14-pv-pgbackup.yaml
   ```
   Also confirm the export paths (`/export/resources`, `/export/pg_data`, `/export/pg_backup`).
2. **Secret** — `cp 02-secret.template.yaml 02-secret.yaml`, set real values. Note: use
   `ADMIN_PASS` (the live `production.env` calls it `ADMIN_PASSWORD`, which `scripts/start` does
   **not** read). `RABBITMQ_URL` creds must match `RABBITMQ_DEFAULT_USER`/`PASS`.
3. **GPU node** — label + taint it (see below).

## NFS server setup (Arbutus)

On the NFS server, export the three dirs to the k3s node IPs (mirrors the current setup —
`rw,sync,no_subtree_check,no_root_squash`; `no_root_squash` is required for the postgres uid 999):
```sh
# /etc/exports  (one line per k3s node IP, per export)
/export/resources   <node-ip>(rw,sync,no_subtree_check,no_root_squash)
/export/pg_data     <node-ip>(rw,sync,no_subtree_check,no_root_squash)
/export/pg_backup   <node-ip>(rw,sync,no_subtree_check,no_root_squash)
sudo exportfs -ra && sudo exportfs -v
```
Verify from each node: `sudo mount -t nfs4 <nfs-ip>:/export/resources /mnt && ls /mnt && umount /mnt`.
This is the #1 failure point — if a node can't mount, its pods stay `ContainerCreating`.

## GPU node setup

1. Install the NVIDIA driver (**≥ 460.x**, required by the CUDA 11.2 `gpu-celery` image) and the
   nvidia-container-toolkit; join the node to k3s. k3s auto-detects the nvidia runtime in containerd.
2. Label and taint:
   ```sh
   kubectl label node <gpu-node> gpu=true
   kubectl taint node <gpu-node> nvidia.com/gpu=present:NoSchedule
   ```
3. `60-nvidia-device-plugin.yaml` then makes the node advertise `nvidia.com/gpu`. If k3s exposes
   the runtime only as a RuntimeClass (not the node default), uncomment `runtimeClassName: nvidia`
   in `33-gpu-celery.yaml` and the device plugin.

## Data migration

Run with the old stack still serving, then a final pass during a short maintenance window.

```sh
# resources (~883 GB) — old NFS export -> new Arbutus export
rsync -aHAX --info=progress2 \
  root@192.168.17.244:/var/lib/docker/volumes/rodan_resources/_data/ \
  /export/resources/
# repeat for a quick incremental pass right before cutover

# pg_data (~4.1 GB, PG 9.6 preserved) — STOP the old postgres first, then raw-copy:
rsync -aHAX root@192.168.17.244:/var/lib/docker/volumes/rodan_pg_data/_data/ /export/pg_data/
# Fallback / verification: pg_dump on the old DB and restore into the new postgres pod instead.
```
After copying, sanity-check: `ls /export/resources/projects | wc -l` should be ~309.

## Apply order

```sh
kubectl apply -f 00-namespace.yaml
kubectl apply -f 01-configmap.yaml -f 02-secret.yaml
kubectl apply -f 10-pv-resources.yaml -f 11-pvc-resources.yaml \
              -f 12-pv-pgdata.yaml -f 13-pvc-pgdata.yaml \
              -f 14-pv-pgbackup.yaml -f 15-pvc-pgbackup.yaml
kubectl -n rodan get pvc            # all Bound before continuing

kubectl apply -f 20-postgres.yaml -f 21-redis.yaml -f 22-rabbitmq.yaml
kubectl apply -f 60-nvidia-device-plugin.yaml
kubectl apply -f 30-rodan-main.yaml          # watch logs: migrate -> collectstatic -> gunicorn
kubectl apply -f 31-celery.yaml -f 32-py3-celery.yaml -f 33-gpu-celery.yaml
kubectl apply -f 40-iipsrv.yaml -f 41-rodan-client.yaml -f 50-nginx.yaml -f 51-ingress.yaml
```
(Or just `kubectl apply -f .` once `02-secret.yaml` and placeholders are filled — ordering is
self-healing via the `wait-for-app` logic baked into the images, but applying backends first is cleaner.)

## Verify

```sh
kubectl -n rodan get pods,svc,pvc,ingress
kubectl -n rodan exec deploy/rodan-main -- curl -s -o /dev/null -w '%{http_code}\n' \
  -H 'User-Agent: k8s' localhost:8000/api/?format=json        # 200
kubectl -n rodan exec deploy/celery     -- celery inspect ping -A rodan --workdir /code/Rodan -d celery@celery
kubectl -n rodan exec deploy/py3-celery -- celery inspect ping -A rodan --workdir /code/Rodan -d celery@Python3
kubectl -n rodan exec deploy/gpu-celery -- celery inspect ping -A rodan --workdir /code/Rodan -d celery@GPU
kubectl -n rodan exec deploy/gpu-celery -- nvidia-smi
kubectl describe node <gpu-node> | grep nvidia.com/gpu       # allocatable: 1
# external (through the edge): https://rodan2.simssa.ca  — log in, open a project/image, run a workflow
```

## Notes / gotchas

- **Postgres on NFS** is preserved per decision — keep replicas=1 and the `hard` mount. Don't scale it.
- **Celery node names** are fixed (`-n "${CELERY_JOB_QUEUE}"`); fine at 1 replica each. To scale a
  worker, change the image's `start-celery` to use a per-pod name (`%h`) first.
- **Large uploads** (nginx allows 700m): if uploads fail at the edge/Traefik, add a Traefik
  middleware raising `maxRequestBodyBytes` (Traefik streams by default, so usually fine).
- **WebSockets** (`/ws/`): if long-lived sockets drop, raise Traefik's responding read timeout.
- **TLS**: none inside the cluster — the edge must send `X-Forwarded-Proto: https` and the correct
  `Host` so Django builds https URLs (nginx already sets `X-Scheme: https` on `/api`).
- **Backups**: the old monthly pg-backup cron appears stopped (~Sep 2024). Consider a k8s CronJob
  invoking the image's `backup` script against `/backups`.
