#!/bin/bash

if [ -z "$(ls -A /var/lib/postgresql/data)" ]; then
  until pg_basebackup -h postgres -U postgres -D /var/lib/postgresql/data -Fp -Xs -R; do
    echo "Primary 대기 중..."
    sleep 2
  done
  chown -R postgres:postgres /var/lib/postgresql/data
  chmod 700 /var/lib/postgresql/data
fi

exec gosu postgres postgres -c config_file=/etc/postgresql/postgresql.conf