#!/bin/bash

dt=`date '+%Y-%m-%d_%H:%M:%S'`

if [ ! -d 'test_log' ]; then
    mkdir test_log
fi

echo 'Input the amount of connections you want to test'
read amount

echo 'Input the number of messages per connection'
read num

echo 'Please enter the server you would like to test on'
options=("rodan.simssa.ca" "rodan-dev.simssa.ca" "localhost")
select server in "${options[@]}";
do
    case $server in
        "rodan.simssa.ca")
            thor --amount $amount --messages $num ws://$server/ws/ > ./test_log/$dt.txt
            break
            ;;
        "rodan-dev.simssa.ca")
            thor --amount $amount --messages $num ws://$server/ws/ > ./test_log/$dt.txt
            break
            ;;
        "localhost")
            thor --amount $amount --messages $num ws://$server:8000/ws/ > ./test_log/$dt.txt
            break
            ;;
        *) echo Invalid option;;
    esac
done
