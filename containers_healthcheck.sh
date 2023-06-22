#!/bin/bash


#Check whether volumes are properly mounted on containers 
#for staging:
# sudo docker inspect --format '{{json .Spec.TaskTemplate.ContainerSpec.Mounts}}' rodan_rodan-main 
#for local
docker inspect --format "{{ .Mounts }}" rodan-rodan-main-1 #


#Check whether ports are exposed in each containers