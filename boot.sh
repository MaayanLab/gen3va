#!/usr/bin/env bash

adduser --disabled-password --gecos '' r
cd /geneva/
mod_wsgi-express setup-server wsgi.py --port=80 --user r --group r --server-root=/etc/geneva --socket-timeout=600 --limit-request-body=524288000
chmod a+x /etc/geneva/handler.wsgi
chown -R r /geneva/geneva/static/
/etc/geneva/apachectl start
tail -f /etc/geneva/error_log