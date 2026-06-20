.PHONY: help setup up down restart logs shell db-shell odoo-shell update-odoo clean build install-deps

help: ## Muestra esta ayuda
	@echo "Comandos disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Configura el proyecto inicialmente
	@echo "🚀 Configurando proyecto..."
	bash scripts/setup.sh
	@echo "✅ Setup completado. No olvides configurar .env con tus credenciales."

up: ## Inicia los servicios Docker
	docker compose up -d

down: ## Detiene los servicios Docker
	docker compose down

restart: ## Reinicia los servicios Docker
	docker compose restart

logs: ## Muestra los logs de Odoo
	docker compose logs -f odoo

logs-db: ## Muestra los logs de la base de datos
	docker compose logs -f db

shell: ## Accede al shell del contenedor de Odoo
	docker compose exec odoo bash

db-shell: ## Accede a la base de datos PostgreSQL
	docker compose exec db psql -U odoo -d postgres

odoo-shell: ## Accede al shell de Python de Odoo
	docker compose exec odoo python3 /mnt/odoo/odoo-bin shell -c /etc/odoo/odoo.conf

update-odoo: ## Actualiza el código de Odoo al último commit
	git submodule update --remote
	@echo "✅ Código de Odoo actualizado"

clean: ## Limpia contenedores, volúmenes y redes
	docker compose down -v
	@echo "✅ Limpieza completada"

build: ## Reconstruye las imágenes Docker
	docker compose build

rebuild: ## Reconstruye y reinicia los servicios
	docker compose up -d --build

install-deps: ## Instala dependencias de Python en el contenedor
	docker compose exec odoo pip3 install -r /mnt/odoo/requirements.txt

backup-db: ## Realiza backup de la base de datos
	docker compose exec db pg_dump -U odoo postgres > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✅ Backup creado"

restore-db: ## Restaura un backup de la base de datos (uso: make restore-db FILE=backup.sql)
	@if [ -z "$(FILE)" ]; then echo "Error: Especifica el archivo con FILE=backup.sql"; exit 1; fi
	docker compose exec -T db psql -U odoo -d postgres < $(FILE)
	@echo "✅ Backup restaurado"

status: ## Muestra el estado de los contenedores
	docker compose ps

test: ## Ejecuta tests de Odoo
	docker compose exec odoo python3 /mnt/odoo/odoo-bin -c /etc/odoo/odoo.conf --test-enable --stop-after-init

update-modules: ## Actualiza la lista de módulos de Odoo
	docker compose exec odoo python3 /mnt/odoo/odoo-bin -c /etc/odoo/odoo.conf --update=all --stop-after-init
