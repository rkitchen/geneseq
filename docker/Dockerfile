FROM ubuntu:14.04
MAINTAINER Michael Laraia <micheal.laraia@gmail.com>
RUN export DEBIAN_FRONTEND=noninteractive && apt-get update && apt-get install -q -y python3 \
   python3-pip \
   uwsgi \
   git \
   vim \
   less \
   screen \
   supervisor
RUN git clone https://github.com/miclaraia/geneseq.git /usr/local/lib/geneseq
RUN mkdir -p /var/run/uwsgi /var/log/supervisor /var/log/uwsgi && useradd -d /dev/null -s /bin/bash http && chown -R http:http /var/log/uwsgi /usr/local/lib/geneseq

RUN rsync -vr /usr/local/lib/geneseq/system_configs/. /
RUN service mysql start || echo "CREATE DATABASE gene_locale" | mysql -u root || service mysql stop
RUN ln -s /usr/bin/pip3 /usr/bin/pip && pip install -r /usr/local/lib/geneseq/pip_requirements.txt

CMD bash -C '/usr/local/bin/startup.sh';'bash'
