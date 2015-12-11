#!/usr/bin/env bash

adduser --disabled-password --gecos '' r
cd /gen3va/
mod_wsgi-express setup-server wsgi.py --port=80 --user r --group r --server-root=/etc/gen3va --socket-timeout=600 --limit-request-body=524288000
chmod a+x /etc/gen3va/handler.wsgi
chown -R r /gen3va/gen3va/static/
/etc/gen3va/apachectl start
tail -f /etc/gen3va/error_log