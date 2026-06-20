#!/bin/bash
# Script de inicialización para el proyecto Odoo
# Este script configura el entorno automáticamente al clonar el proyecto

set -e

echo "🚀 Inicializando proyecto Odoo..."

# Verificar si git está instalado
if ! command -v git &> /dev/null; then
    echo "❌ Error: git no está instalado"
    exit 1
fi

# Inicializar y actualizar submodules
echo "📦 Actualizando submodules (código de Odoo)..."
git submodule update --init --recursive

# Crear archivo .env si no existe
if [ ! -f .env ]; then
    echo "🔐 Creando archivo .env..."
    cat > .env << EOF
# Configuración de base de datos
POSTGRES_DB=postgres
POSTGRES_USER=odoo
POSTGRES_PASSWORD=odoo

# Configuración de Odoo
ODOO_ADMIN_PASSWORD=admin
ODOO_HOST=db
ODOO_PORT=8069
EOF
    echo "✅ Archivo .env creado (por favor cambia las contraseñas)"
else
    echo "✅ Archivo .env ya existe"
fi

# Crear estructura de carpetas para custom_addons
echo "📁 Creando estructura de carpetas para custom_addons..."
mkdir -p custom_addons/{core,integrations,utils,themes}
mkdir -p enterprise

# Crear archivos .gitkeep si no existen
for dir in custom_addons/core custom_addons/integrations custom_addons/utils custom_addons/themes enterprise; do
    if [ ! -f "$dir/.gitkeep" ]; then
        touch "$dir/.gitkeep"
    fi
done

echo "✅ Estructura de carpetas creada"

# Crear directorio de logs si no existe
mkdir -p logs

echo "✅ Setup completado exitosamente"
echo ""
echo "📝 Próximos pasos:"
echo "   1. Revisa y modifica .env con tus credenciales reales"
echo "   2. Ejecuta: docker-compose up -d"
echo "   3. Accede a Odoo en http://localhost:8069"
