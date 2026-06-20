#!/bin/bash
# ./odoo/entrypoint.sh

set -e

echo "Esperando base de datos..."
while ! nc -z db 5432; do
  sleep 1
done
echo "Base de datos lista"

if [ "$ENABLE_DEBUG" = "true" ]; then
  echo "Iniciando con debug..."
  exec python3 -Xfrozen_modules=off -m debugpy --listen 0.0.0.0:5678 /usr/bin/odoo -c /etc/odoo/odoo.conf
else
  echo "Iniciando Odoo..."
  exec odoo -c /etc/odoo/odoo.conf
fi