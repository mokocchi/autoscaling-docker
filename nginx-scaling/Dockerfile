FROM nginx:alpine AS builder

# Download sources
RUN wget "http://nginx.org/download/nginx-${NGINX_VERSION}.tar.gz" -O nginx.tar.gz && \
  wget "https://github.com/vozlt/nginx-module-vts/archive/refs/tags/v0.1.18.tar.gz" -O nginx-module-vts.tar.gz

RUN apk add --no-cache --virtual .build-deps \
  gcc \
  libc-dev \
  make \
  openssl-dev \
  pcre-dev \
  zlib-dev \
  linux-headers \
  libxslt-dev \
  gd-dev \
  geoip-dev \
  perl-dev \
  libedit-dev \
  mercurial \
  bash \
  alpine-sdk \
  findutils

# Reuse same cli arguments as the nginx:alpine image used to build
RUN CONFARGS=$(nginx -V 2>&1 | sed -n -e 's/^.*arguments: //p') \
  mkdir /usr/src && \
  tar -zxC /usr/src -f nginx.tar.gz && \
  tar -xzvf "nginx-module-vts.tar.gz" && \
  VTSDIR="/nginx-module-vts-0.1.18" && \
  cd /usr/src/nginx-$NGINX_VERSION && \
  ./configure --with-compat $CONFARGS --add-dynamic-module=$VTSDIR && \
  make && make install

FROM nginx:alpine
COPY --from=builder /usr/local/nginx/modules/ngx_http_vhost_traffic_status_module.so /usr/local/nginx/modules/ngx_http_vhost_traffic_status_module.so
RUN apk add python3 py-pip py-virtualenv py-flask uwsgi-python3

RUN mkdir /usr/src
WORKDIR /usr/src
RUN python3 -m venv instances-listener && chmod 744 ./instances-listener/bin/activate && ./instances-listener/bin/activate

WORKDIR /usr/src/instances-listener

COPY instances-listener/app.py /usr/src/instances-listener/app.py
COPY instances-listener/wsgi.py /usr/src/instances-listener/wsgi.py

COPY nginx.template /etc/nginx/conf.d/nginx.template
RUN mv /etc/nginx/nginx.conf /etc/nginx/nginx.old

EXPOSE 80 5000

STOPSIGNAL SIGQUIT

RUN echo 'load_module /usr/local/nginx/modules/ngx_http_vhost_traffic_status_module.so;' > /etc/nginx/nginx.conf \
    && sed 's/http {/http {@    vhost_traffic_status_zone;@    vhost_traffic_status_filter_by_host on;@/' /etc/nginx/nginx.old | tr '@' '\n' >> /etc/nginx/nginx.conf

CMD ["/bin/sh", "-c", "export uri=uri remote_addr=remote_addr http_host=http_host && envsubst < /etc/nginx/conf.d/nginx.template > /etc/nginx/conf.d/default.conf \
    && uwsgi --socket 0.0.0.0:3031 --plugins python3 --protocol http --wsgi wsgi:app & nginx -g 'daemon off;'"]


