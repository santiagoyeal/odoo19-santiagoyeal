# Proyecto Odoo 19.0

Proyecto Odoo 19.0 con configuración Docker y mejores prácticas de desarrollo SOLID.

## 📁 Estructura del Proyecto

```
odoo19-santiagoyeal/
├── custom_addons/          # Addons personalizados (SOLID)
│   ├── core/              # Módulos core del negocio
│   ├── integrations/      # Integraciones con terceros
│   ├── utils/             # Utilidades compartidas
│   └── themes/            # Temas personalizados
├── enterprise/            # Addons enterprise
├── odoo_src/              # Código fuente de Odoo (git submodule)
├── odoo/                  # Configuración Docker de Odoo
│   ├── Dockerfile
│   ├── entrypoint.sh
│   └── odoo.conf
├── scripts/               # Scripts de utilidad
│   └── setup.sh          # Script de inicialización
├── data/                  # Datos persistentes
├── logs/                  # Logs de la aplicación
├── docker-compose.yml     # Configuración Docker Compose
├── .env.example           # Ejemplo de variables de entorno
└── .gitignore            # Archivos ignorados por git
```

## 🚀 Configuración Inicial

### 1. Clonar el repositorio con submodules

```bash
git clone --recurse-submodules <tu-repo-url>
cd odoo19-santiagoyeal
```

Si ya clonaste sin submodules:

```bash
git submodule update --init --recursive
```

### 2. Ejecutar script de inicialización

```bash
bash scripts/setup.sh
```

Este script:
- Actualiza los submodules
- Crea el archivo `.env` con valores por defecto
- Crea la estructura de carpetas para custom_addons
- Crea directorios necesarios

### 3. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con tus credenciales reales
```

**IMPORTANTE:** Cambia las contraseñas por defecto en `.env`:
- `POSTGRES_PASSWORD`: Contraseña de PostgreSQL
- `ODOO_ADMIN_PASSWORD`: Contraseña de administrador de Odoo

## 🐳 Ejecutar el Proyecto

### Iniciar servicios

```bash
docker compose up --build
```

### Ver logs

```bash
docker compose logs -f odoo
```

### Detener servicios

```bash
docker compose down
```

### Reiniciar servicios

```bash
docker compose restart
```

## 📝 Estructura de Custom Addons (SOLID)

El proyecto sigue principios SOLID para la organización de addons:

- **core/**: Módulos core del negocio (Single Responsibility)
- **integrations/**: Integraciones con APIs de terceros (Open/Closed)
- **utils/**: Utilidades compartidas y helpers (Dependency Inversion)
- **themes/**: Temas personalizados (Interface Segregation)

## 🔐 Seguridad

- Las credenciales se gestionan mediante variables de entorno (`.env`)
- El archivo `.env` está en `.gitignore`
- Se proporciona `.env.example` como plantilla
- El código de Odoo se gestiona mediante git submodule

## 🛠️ Comandos Útiles

### Actualizar código de Odoo

```bash
git submodule update --remote
```

### Acceder al contenedor de Odoo

```bash
docker compose exec odoo bash
```

### Acceder a la base de datos

```bash
docker compose exec db psql -U odoo -d postgres
```

### Reiniciar Odoo

```bash
docker compose restart odoo
```

## 📚 Recursos

- [Documentación de Odoo](https://www.odoo.com/documentation/19.0/)
- [Docker Odoo](https://hub.docker.com/_/odoo)
- [Git Submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules)

## 🤝 Contribución

1. Crea una rama para tu feature
2. Commit tus cambios
3. Push a la rama
4. Abre un Pull Request

## 📄 Licencia

Este proyecto es propietario. El código de Odoo está bajo licencia LGPL-3.
