#!/bin/sh

( rabbitmqctl wait $RABBITMQ_PID_FILE && \
    rabbitmqctl add_user $HPC_RABBITMQ_USER $HPC_RABBITMQ_PASSWORD && \
    rabbitmqctl set_permissions $HPC_RABBITMQ_USER ".*" ".*" ".*" ) &
rabbitmq-server $@
