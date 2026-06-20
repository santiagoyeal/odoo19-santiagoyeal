# ./odoo/Dockerfile
ARG ODOO_VERSION=19.0
FROM odoo:$ODOO_VERSION

USER root

RUN apt-get update \
 && apt-get install -y git python3-pip netcat-openbsd \
 && pip3 install debugpy --break-system-packages

# Copiar el script (que ya existe en tu sistema)
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

USER odoo

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]