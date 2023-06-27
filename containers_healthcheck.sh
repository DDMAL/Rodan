#!/bin/bash


#Check whether volumes are properly mounted on containers 
#for staging:
 #get all mounts information for containers 
for CONTAINER in $(sudo docker ps -aq);
do 
    name=$(sudo docker inspect --format " {{.Name}}" $CONTAINER)
    if [[ "$name" == *"rabbit"* ||  "$name" == *"redis"* || "$name" == *"postgres"* ]]; then
        continue 
    fi
    mount_list=$(sudo docker inspect --format  " {{json .Mounts }}" $CONTAINER )

    IFS='{}[]' read -r -a a <<< $mount_list
    array=( $a ) #separate mounts and reconstruct an array
    binds=()
    echo $name
    for mount in "${array[@]}";
    do
        if [[ "$mount" == "," ]]; then 
            continue
        fi
        # binds+=("$m")
        IFS=',' read -r -a b <<< $mount
        for e in $b
        do 
            if [[ "$e" == *"Name"* ]]; then
                if [[ "$e" == "\"Name\":\"rodan_resources\"" ]]; then
                    echo good
                fi
            fi

        done
    done
    # echo "${binds[@]}" #now each bind is a json string 

done
