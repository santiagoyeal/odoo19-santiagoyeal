ARG ODOO_VERSION=19.0
FROM odoo:$ODOO_VERSION

USER root

RUN apt-get update && apt-get install -y git python3-pip && pip3 install debugpy

USER odoo
