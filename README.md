# FastManage

## 1. Nombre del proyecto

**FastManage — Sistema de gestión de restaurantes, locales, empleados y asignaciones laborales.**

## 2. Descripción

FastManage es una aplicación web destinada a administrar información de restaurantes y sus sucursales, registrar empleados y gestionar las asignaciones del personal a los diferentes locales.

El sistema dispone de registro e inicio de sesión, un panel de control (*dashboard*) y módulos para consultar, crear y actualizar información. También permite desactivar empleados y finalizar asignaciones de forma lógica, conservando los registros históricos para su posterior consulta.

Sus módulos principales son:

- **Autenticación:** registro, inicio y cierre de sesión.
- **Dashboard:** resumen de restaurantes, locales, empleados y asignaciones.
- **Restaurantes:** administración de establecimientos.
- **Locales:** administración de sucursales vinculadas a restaurantes.
- **Empleados:** registro, actualización y desactivación lógica del personal.
- **Asignaciones:** vinculación de empleados con locales, gestión de turnos y conservación del historial laboral.

## 3. Tecnologías utilizadas

| Componente | Tecnología |
| --- | --- |
| Lenguaje del backend | Python |
| Framework de la API | FastAPI |
| Servidor de desarrollo | Uvicorn |
| Persistencia de datos | SQLite |
| ORM | SQLAlchemy |
| Validación de datos | Pydantic |
| Frontend | HTML5, CSS3 y JavaScript |
| Comunicación cliente-servidor | API REST y `fetch` |
| Autenticación | JWT mediante cookies HttpOnly |
| Protección de solicitudes | Token CSRF |
| Pruebas automatizadas (previstas) | pytest y HTTPX |

## 4. Instrucciones para instalar el proyecto

### Requisitos previos

- Tener **Python 3** instalado y disponible desde la terminal.
- Disponer de **pip** para instalar dependencias.
- Utilizar una terminal como **CMD** o PowerShell en Windows.
- Contar con un navegador web actualizado.

### Paso 1. Abrir la carpeta del proyecto

En CMD, navega hasta el directorio donde se encuentra FastManage:

```bat
cd "C:\Users\TICS 206-19\Documents\ProyectoPython-David"
```

Si guardaste el proyecto en otra ubicación, modifica la ruta según corresponda.

### Paso 2. Crear el entorno virtual

```bat
python -m venv .venv
```

### Paso 3. Activar el entorno virtual

En **CMD**:

```bat
.venv\Scripts\activate
```

En **PowerShell**:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Paso 4. Instalar las dependencias

```bat
python -m pip install -r requirements.txt
```

### Paso 5. Configurar las variables de entorno

Si todavía no existe el archivo `.env`, crea una copia de `.env.example`:

```bat
copy .env.example .env
```

Revisa las variables definidas en `.env` y configura los valores necesarios para tu entorno, especialmente la clave secreta utilizada para firmar los JWT. Para el desarrollo local con HTTP, la configuración de cookies debe ser compatible con ese entorno; en producción deben utilizarse HTTPS y cookies seguras.

> **Importante:** no compartas el archivo `.env` ni incluyas claves secretas reales en repositorios públicos.

### Paso 6. Base de datos

El proyecto utiliza **SQLite**, por lo que no es necesario instalar un servidor de base de datos adicional. La base de datos de desarrollo se encuentra en `data/fastmanage.db` cuando ya ha sido creada.

Si el proyecto se instala desde cero, comprueba que se haya aplicado el mecanismo de creación de tablas y las migraciones incluidas en `migrations/`, según la configuración del backend. No ejecutes migraciones sobre datos importantes sin realizar una copia de seguridad.

## 5. Instrucciones para ejecutar el proyecto

### Paso 1. Activar el entorno virtual

Desde la raíz del proyecto, si aún no está activado:

```bat
.venv\Scripts\activate
```

### Paso 2. Iniciar el servidor

```bat
python -m uvicorn backend.main:app --reload
```

El servidor de desarrollo estará disponible normalmente en:

**http://127.0.0.1:8000/**

### Paso 3. Acceder a la aplicación

Abre las siguientes direcciones en el navegador:

| Sección | Dirección |
| --- | --- |
| Inicio | `http://127.0.0.1:8000/` |
| Inicio de sesión | `http://127.0.0.1:8000/login.html` |
| Registro | `http://127.0.0.1:8000/registro.html` |
| Dashboard | `http://127.0.0.1:8000/dashboard.html` |
| Restaurantes | `http://127.0.0.1:8000/restaurantes.html` |
| Locales | `http://127.0.0.1:8000/locales.html` |
| Empleados | `http://127.0.0.1:8000/empleados.html` |
| Asignaciones | `http://127.0.0.1:8000/asignaciones.html` |
| Documentación de la API | `http://127.0.0.1:8000/docs` |

Las páginas administrativas requieren una sesión autenticada para consultar y modificar datos.

### Paso 4. Detener el servidor

En la terminal donde se ejecuta Uvicorn, presiona:

```text
Ctrl + C
```

> El parámetro `--reload` se recomienda únicamente para desarrollo. Para desplegar el proyecto en producción deben revisarse la configuración de seguridad, HTTPS y el servidor de aplicaciones.

## 6. Estructura general del sistema

```text
ProyectoPython-David/
│
├── backend/
│   ├── __init__.py
│   ├── main.py                 # Aplicación FastAPI y rutas de páginas
│   ├── config.py               # Configuración general
│   ├── database.py             # Conexión y sesión de base de datos
│   ├── security.py             # Utilidades de seguridad
│   ├── dependencies.py         # Dependencias de autenticación y API
│   │
│   ├── models/                 # Modelos SQLAlchemy
│   │   ├── usuario.py
│   │   ├── restaurante.py
│   │   ├── local.py
│   │   ├── empleado.py
│   │   └── asignacion.py
│   │
│   ├── schemas/                # Esquemas Pydantic
│   │   ├── usuario.py
│   │   ├── restaurante.py
│   │   ├── local.py
│   │   ├── empleado.py
│   │   └── asignacion.py
│   │
│   └── routers/                # Endpoints de la API REST
│       ├── auth.py
│       ├── restaurantes.py
│       ├── locales.py
│       ├── empleados.py
│       └── asignaciones.py
│
├── frontend/
│   ├── pages/                  # Páginas HTML
│   │   ├── index.html
│   │   ├── login.html
│   │   ├── registro.html
│   │   ├── dashboard.html
│   │   ├── restaurantes.html
│   │   ├── locales.html
│   │   ├── empleados.html
│   │   └── asignaciones.html
│   │
│   ├── css/                    # Hojas de estilos
│   │   ├── styles.css
│   │   ├── auth.css
│   │   ├── dashboard.css
│   │   └── formularios.css
│   │
│   ├── js/                     # Lógica del frontend
│   │   ├── api.js
│   │   ├── auth.js
│   │   ├── dashboard.js
│   │   ├── restaurantes.js
│   │   ├── locales.js
│   │   ├── empleados.js
│   │   └── asignaciones.js
│   │
│   └── assets/                 # Recursos estáticos
│
├── data/
│   └── fastmanage.db           # Base de datos SQLite local
│
├── migrations/                 # Scripts de migración
├── tests/                      # Pruebas del proyecto
├── .env.example                # Plantilla de configuración
├── .env                        # Configuración local (privada)
├── .gitignore                  # Exclusiones de Git
├── requirements.txt            # Dependencias de Python
└── README.md                   # Documentación del proyecto
```

### Funcionamiento general

1. El usuario abre una página HTML desde el navegador.
2. JavaScript realiza solicitudes a los endpoints `/api/` de FastAPI.
3. FastAPI valida la sesión, los permisos y los datos recibidos.
4. SQLAlchemy interactúa con la base de datos SQLite.
5. La API devuelve respuestas JSON y la interfaz actualiza la información mostrada.

**Nota:** la estructura refleja la organización utilizada durante el desarrollo de FastManage. Los nombres y las validaciones específicas deben mantenerse sincronizados con los archivos definitivos del proyecto.
