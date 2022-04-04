# JSOMR to MEI Wiki

Automated conversion from [`JSOMR`](JSOMR) into [MEI](http://music-encoding.org/) as a job in the workflow builder [```Rodan```](https://github.com/DDMAL/Rodan)

## Prereq

JSOMR to MEI is deployed as a Rodan [Job Package](https://github.com/DDMAL/Rodan/wiki/Write-a-Rodan-job-package). Before installing, ensure that the latestest version of [`rodan-docker`](https://github.com/DDMAL/rodan-docker) has been cloned locally, built, and installed.

## Installing into rodan-docker
1. Clone this directory into `/path/to/rodan_docker/jobs/JSOMR2MEI`
2. In `/path/to/rodan_docker/docker-compose.job-dev.yml`, add the reference to volumes like so:
``` python
    volumes:
     - ./jobs/settings.py:/code/rodan/rodan/settings.py
     - ./jobs/JSOMR2MEI/:/code/rodan/rodan/jobs/JSOMR2MEI
```
3. If one does not already exist, create a python file called `settings.py` in the rodan jobs folder like so: `/path/to/rodan_docker/jobs/settings.py`
4. Copy and paste the contents of `settings.py.job_development` into `settings.py`
5. Add this package path to the Rodan Job Package registration in the `settings.py` file. This should look something like the following
``` python
RODAN_JOB_PACKAGES = (
  "rodan.jobs.job1",
  "rodan.jobs.job2",
  ...,
  "rodan.jobs.JSOMR2MEI",
)
```

## Running Rodan
- Follow the [rodan-docker guide](https://github.com/DDMAL/rodan-docker/blob/master/README.md) to have docker set up.
- Once the above installation steps are complete, run ```docker-compose -f docker-compose.yml -f docker-compose.rodan-dev.yml up``` 