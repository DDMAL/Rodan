# PostgreSQL 9.6 → 16 upgrade runbook

Django 4.2 dropped support for PostgreSQL < 12, so the modernized stack requires Postgres 16.
The image is already on 16 (`postgres/Dockerfile` → `postgres:16-bookworm` + `postgresql-plpython3-16`
+ `python3-redis`). Because 9.6 and 16 on-disk formats are incompatible, PG16 can't start on the
9.6 data files — the data must be **logically dumped from 9.6 and restored into 16**.

This is a **one-time cutover**, run on the NFS/data server **192.168.236.124** (has Docker; the
`dd`-cloned 9.6 cluster lives there). It produces a new `pg16_data` dir alongside the 9.6 clone,
which is kept untouched as rollback. DB `rodan`, role `someadmin`, ~4.1 GB.

> The k8s manifests already target the new datadir: `12-pv-pgdata.yaml` `nfs.path` = `/srv/rodan-data/pg16_data`.
> Do **not** `kubectl apply` the postgres PV/StatefulSet until steps 1–4 below are done.

## 1. Quiesce (never run two servers on one datadir)
```sh
kubectl -n rodan scale statefulset/postgres --replicas=0
kubectl -n rodan scale deploy/rodan-main deploy/celery deploy/py3-celery deploy/gpu-celery --replicas=0
kubectl -n rodan get pods            # confirm no postgres pod
```

## 2. Dump the 9.6 DB (from a copy, keeping the clone pristine)
```sh
cp -a /srv/rodan-data/var/lib/docker/volumes/rodan_pg_data/_data /srv/rodan-data/pg96_src
docker run -d --name pg96 -v /srv/rodan-data/pg96_src:/var/lib/postgresql/data ddmal/postgres-plpython:v3.3.1
until docker exec pg96 pg_isready -U someadmin -q; do sleep 1; done
docker exec pg96 pg_dump -U someadmin -d rodan --no-owner --no-privileges -Fc -f /tmp/rodan.dump
docker cp pg96:/tmp/rodan.dump /srv/rodan-data/rodan.dump
docker rm -f pg96
```

## 3. Init PG16 on a new datadir and restore
```sh
mkdir -p /srv/rodan-data/pg16_data
docker run -d --name pg16 \
  -e POSTGRES_USER=someadmin -e POSTGRES_PASSWORD=123456Seven -e POSTGRES_DB=rodan \
  -v /srv/rodan-data/pg16_data:/var/lib/postgresql/data ddmal/postgres-plpython:py311test
until docker exec pg16 pg_isready -U someadmin -q; do sleep 1; done
docker cp /srv/rodan-data/rodan.dump pg16:/tmp/rodan.dump
docker exec pg16 pg_restore -U someadmin -d rodan --no-owner --no-privileges /tmp/rodan.dump
docker exec pg16 psql -U someadmin -d rodan -c "SELECT count(*) FROM auth_user;"   # expect 129
docker rm -f pg16
```
- The dump's `publish_message` (plpython3u) + `object_notify` triggers restore fine on PG16 (it has
  `plpython3-16` + `python3-redis`). If any plpython object errors, ignore it — `rodan/models/__init__.py`
  re-creates the function/triggers at app startup.

## 4. Export the new datadir + recreate the k8s PV/PVC
On 192.168.236.124 `/etc/exports` (then `sudo exportfs -ra`):
```
/srv/rodan-data/pg16_data  192.168.236.0/24(rw,sync,no_subtree_check,no_root_squash)
```
The NFS source on a PV is immutable, so recreate (Retain policy leaves both data dirs intact):
```sh
kubectl -n rodan delete pvc rodan-pg-data ; kubectl delete pv rodan-pg-data-pv
kubectl apply -f k8s/12-pv-pgdata.yaml -f k8s/13-pvc-pgdata.yaml
```

## 5. Deploy PG16 image + bring the stack back
Ensure `20-postgres.yaml`'s image is the CI-published PG16 tag (`ghcr.io/ddmal/postgres-plpython:<tag>`).
```sh
kubectl apply -f k8s/20-postgres.yaml
kubectl -n rodan scale statefulset/postgres --replicas=1
kubectl -n rodan rollout status statefulset/postgres
kubectl -n rodan scale deploy/rodan-main deploy/celery deploy/py3-celery --replicas=1
```
`scripts/start` runs `manage.py migrate` → applies **0006** (widens `User.first_name`; the `view_` rows
already exist so `create_permissions` is a no-op) and re-establishes the plpython trigger.

## Verify
```sh
kubectl -n rodan exec statefulset/postgres -- psql -U someadmin -d rodan -c "SHOW server_version;"   # 16.x
kubectl -n rodan exec statefulset/postgres -- psql -U someadmin -d rodan -c "SELECT count(*) FROM auth_user;"  # 129
kubectl -n rodan exec deploy/rodan-main -- curl -s -o /dev/null -w '%{http_code}\n' -H 'User-Agent: k8s' localhost:8000/api/?format=json  # 200
```

## Rollback
The original 9.6 datadir (`.../rodan_pg_data/_data`) is never modified (dump ran from `pg96_src`; the PV
is `Retain`). Reverting means re-pointing the PV to it **and** reverting the `modernize-backend-py311`
branch (the Django-4.2 app cannot run on 9.6).
