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
   && useradd -d /dev/null -s /bin/bash http \
   && mkdir -p /var/run/uwsgi \
               /var/log/supervisor \
               /var/log/uwsgi
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
   && useradd -d /dev/null -s /bin/bash http \
   && mkdir -p /var/run/uwsgi \
               /var/log/supervisor \
               /var/log/uwsgi
   && chown -R http:http /var/log/uwsgi \

RUN rsync -vr /usr/local/lib/geneseq/system_configs/. /
RUN service mysql start || echo "CREATE DATABASE gene_locale" | mysql -u root || service mysql stop
RUN pip install -r /usr/local/lib/geneseq/pip_requirements.txt

CMD bash -C '/usr/local/bin/startup.sh';'bash'
   && chown -R http:http /var/log/uwsgi \
COPY ../../pip_requirements.txt /tmp/
RUN pip3 install < /tmp/pip_requirements.txt
