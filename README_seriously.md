# How to run for M1

- Download the most recent images using `make pull` -- you may want to `make clean` first

- Then run `docker build --no-cache --tag nginx-local nginx` 

- `make run` as usual. 

- `docker-compose exec rodan-main bash` and `pip uninstall tensorflow && pip uninstall tensorflow-estimator` 
    - TensorFlow may already be uninstalled but double check.

- `/run/start` 