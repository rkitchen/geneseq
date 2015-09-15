FROM ubuntu:14.04
MAINTAINER Michael Laraia <micheal.laraia@gmail.com>
RUN export DEBIAN_FRONTEND=noninteractive && \
   apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10 \
   echo "deb http://repo.mongodb.org/apt/ubuntu "$(lsb_release -sc)"/mongodb-org/3.0 multiverse" | \
   tee /etc/apt/sources.list.d/mongodb-org-3.0.list \
   apt-get update && apt-get install -q -y python3 \
   python3-pip \
   uwsgi-plugin-python3 \
   curl \
   uwsgi \
   git \
   vim \
   less \
   screen \
   supervisor \
   mongodb-org \
   && useradd -d /dev/null -s /bin/bash http \
   && mkdir -p /var/run/uwsgi \
               /var/log/supervisor \
               /var/log/uwsgi \
   && chown -R http:http /var/log/uwsgi


COPY pip_requirements.txt /tmp/
RUN pip3 install -r /tmp/pip_requirements.txt
