FROM prom/prometheus:latest as builder

FROM alpine:latest

RUN apk add --no-cache python3 py-pip py-virtualenv py-flask uwsgi-python3 py3-yaml 
RUN apk add --no-cache py3-flask-cors -X http://dl-cdn.alpinelinux.org/alpine/edge/testing

COPY --from=builder /bin/prometheus        /bin/prometheus
COPY --from=builder /bin/promtool          /bin/promtool
COPY config-listener/prometheus.yml         /etc/prometheus/prometheus.yml
COPY config-listener/alert.rules.yml        /etc/prometheus/alert.rules.yml

RUN mkdir -p /prometheus && \
    chown -R nobody:nobody etc/prometheus /prometheus

RUN mkdir /usr/src
WORKDIR /usr/src
COPY config-listener/app.py /usr/src/config-listener/app.py
COPY config-listener/wsgi.py /usr/src/config-listener/wsgi.py

WORKDIR /usr/src/config-listener

USER       nobody
EXPOSE     9090

CMD ["/bin/sh", "-c", "uwsgi --socket 0.0.0.0:3031 --uid nobody --plugins python3 --protocol http --wsgi wsgi:app & cd /prometheus \
    && /bin/prometheus \
    --config.file=/etc/prometheus/prometheus.yml \
    --storage.tsdb.path=/prometheus \
    --web.console.libraries=/usr/share/prometheus/console_libraries \
    --web.console.templates=/usr/share/prometheus/consoles \
    --web.enable-lifecycle" ]