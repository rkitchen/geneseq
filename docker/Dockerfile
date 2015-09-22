FROM ubuntu:15.04
MAINTAINER Michael Laraia <micheal.laraia@gmail.com>
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10
RUN echo "deb http://repo.mongodb.org/apt/ubuntu trusty/mongodb-org/3.0 multiverse" > \
   /etc/apt/sources.list.d/mongodb-org-3.0.list
RUN apt-get update && apt-get install -q -y python3 \
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
               /data/db \
               /data/dump \
   && chown -R http:http /var/log/uwsgi


COPY pip_requirements.txt /tmp/
RUN pip3 install -r /tmp/pip_requirements.txt

COPY system_configs /

RUN echo 2

RUN  git clone https://github.com/miclaraia/geneseq.git \
    /usr/local/lib/geneseq && \
    chown -R http:http /usr/local/lib/geneseq

VOLUME ['/data/db']

EXPOSE 8080
#ENTRYPOINT /bin/bash -c "/usr/local/bin/startup.sh; /bin/bash"
