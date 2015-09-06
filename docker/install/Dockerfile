FROM ubuntu:14.04
MAINTAINER Michael Laraia <micheal.laraia@gmail.com>
RUN export DEBIAN_FRONTEND=noninteractive && apt-get update && apt-get install -q -y python3 \
   python3-pip \
   uwsgi \
   git \
   vim \
   less \
   screen \
   supervisor \
   mysql-server \
   && useradd -d /dev/null -s /bin/bash http \
   && mkdir -p /var/run/uwsgi \
               /var/log/supervisor \
               /var/log/uwsgi \
   && chown -R http:http /var/log/uwsgi


COPY pip_requirements.txt /tmp/
RUN pip3 install -r /tmp/pip_requirements.txt
