#!/bin/bash

dt=`date '+%Y-%m-%d_%H:%M:%S'`
amount=10000
number=1
server='localhost:8000'

if [ ! -d 'test_log' ]; then
    mkdir test_log
fi

while getopts 'ha:n:s' flag; do
    case "${flag}" in
        h)
            echo "Options:"
            echo "-a            Number of connections to test on, if unspecified, 10000 connections will be tested"
            echo "-n            Number of messages to be sent per connection"
            echo "-s            Name of the server, eg. rodan.simssa.ca. if unspecified, server will be localhost"
            echo "-h            Show help instructions"
            exit 0
            ;;
        a)  amount=${OPTARG} ;;
        n)  number=${OPTARG} ;;
        s)  server=${OPTARG} ;;
        *)
            echo Invalid argument ${flag}
            exit 0
            ;;
    esac
done

echo "Number of connections tested: $amount" >> ./test_log/$dt.txt
echo "Number of messages sent per connection: $number" >>  ./test_log/$dt.txt
thor --amount $amount --messages $number ws://$server/ws/ >> ./test_log/$dt.txt
echo "Test successfully executed"
exit 0
