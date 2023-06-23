#!/bin/bash


#Check whether volumes are properly mounted on containers 
#for staging:
 #get all mounts information for containers 
for CONTAINER in $(sudo docker ps -aq)
do 
    if [[ $(sudo docker inspect --format " {{.Name}}" $CONTAINER) == *"rabbit"* ]];
    then 
    fi
    mounts=$(sudo docker inspect --format  "{{json .Mounts }}" $CONTAINER )
    echo $mounts 
done
# sudo docker inspect --format "{{.Name}}:      {{json .Mounts }}" $(sudo docker ps -aq) | column -t -s ' '

# #Check whether ports are exposed in each containers

check_mounts(){
    
}

# sudo docker inspect ls --format='{{json .Spec.TaskTemplate.ContainerSpec.Mounts}}' $(sudo docker ps -aq)