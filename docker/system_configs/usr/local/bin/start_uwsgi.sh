#!/bin/bash
/usr/local/bin/check_mongod.sh
/usr/bin/uwsgi --ini /etc/uwsgi/uwsgi.ini
exit 0