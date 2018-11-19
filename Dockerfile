FROM python:3.5.3

COPY ./contribs/docker/certs /usr/share/xivo-certs
RUN true \
    && mkdir -p /etc/wazo-setupd/conf.d \
    && mkdir -p /etc/wazo-nestbox-plugin/conf.d \
    && install -d /var/run/wazo-setupd \
    && touch /var/log/wazo-setupd.log \
    && apt-get -yqq autoremove \
    && openssl req -x509 -newkey rsa:4096 -keyout /usr/share/xivo-certs/server.key -out /usr/share/xivo-certs/server.crt -nodes -config /usr/share/xivo-certs/openssl.cfg -days 3650

COPY . /usr/src/wazo-setupd
WORKDIR /usr/src/wazo-setupd
RUN true \
  && pip install -r /usr/src/wazo-setupd/requirements.txt \
  && python setup.py install \
  && cp -r etc/* /etc

EXPOSE 9302

CMD ["python3", "-u", "/usr/local/bin/wazo-setupd"]
