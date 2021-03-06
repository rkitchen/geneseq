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
   nodejs \
   npm \
   libffi-dev \
   && useradd -d /dev/null -s /bin/bash http \
   && mkdir -p /var/run/uwsgi \
               /var/log/supervisor \
               /var/log/uwsgi \
               /data/db \
               /data/dump \
   && chown -R http:http /var/log/uwsgi \
   && npm install mongo-express

VOLUME ['/data/db']

EXPOSE 8080
ENTRYPOINT /bin/bash -c "supervisord; /bin/bash"

COPY pip_requirements.txt /tmp/
RUN pip3 install -r /tmp/pip_requirements.txt

COPY system_configs /

RUN echo 1

RUN  git clone https://github.com/rkitchen/geneseq.git \
    /opt/geneseq && \
    chown -R http:http /opt/geneseq && \
    ln -s /opt/geneseq/source /usr/local/lib/geneseq && \
    ln -s /opt/geneseq/data/update_processed.py /usr/local/bin/update_processed && \
    ln -s /opt/geneseq/data/update_mouse_expression.py /usr/local/bin/update_mouse_expression && \
    ln -s /opt/geneseq/data/update_annotations.py /usr/local/bin/update_annotations
