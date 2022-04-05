FROM rabbitmq:alpine
ARG VERSION

COPY ./config/rabbitmq.conf /etc/rabbitmq/
COPY ./scripts/setup.sh /run/setup.sh
RUN chmod +x /run/setup.sh

CMD ["/run/setup.sh"]
