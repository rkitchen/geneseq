#!/bin/bash

/usr/bin/mysqld_safe &
# Time out in 1 minute
LOOP_LIMIT=60
for (( i=0 ; ; i++ )); do
    if [ ${i} -eq ${LOOP_LIMIT} ]; then
        echo "Time out. Error log is shown as below:"
        exit 1
    fi
    echo "=> Waiting for confirmation of MySQL service startup, trying ${i}/${LOOP_LIMIT} ..."
    sleep 1
    mysql -uroot -e "status" && break
done
exit 0
