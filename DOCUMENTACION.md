# Documentación del Proyecto — Metodología de Sistemas II

## 1. Descripción general

Aplicación web de e-commerce desarrollada como Trabajo Práctico Integrador para la asignatura **Metodología de Sistemas II (UTN)**. Permite a usuarios finales registrarse, navegar un catálogo de productos, gestionar un carrito y finalizar compras; e incluye un panel de administración para gestionar productos y consultar el historial de compras.

El backend está construido con **Django** y delega la persistencia de los datos de negocio en **Supabase** (PostgreSQL gestionado + Auth + Storage). SQLite se mantiene únicamente para las tablas internas de Django (sesiones, mensajes, etc.).

---

## 2. Stack tecnológico

| Capa | Tecnología |
|------|-----------|
| Lenguaje | Python 3.13 |
| Framework web | Django 4.2.25 |
| Auth + DB + Storage | Supabase (`supabase`, `supabase-auth`) |
| Servidor estático | WhiteNoise 6.11.0 |
| Servidor WSGI (prod) | Gunicorn 23.0.0 |
| Variables de entorno | python-dotenv 1.1.1 |
| Frontend | HTML + CSS + JS (plantilla **HTML5UP Editorial**), jQuery |
| Base local | SQLite (solo Django interno) |
| Despliegue | Render.com (`metodologia-jv74.onrender.com`) |
| Tests | Django TestCase + `unittest.mock` |

Dependencias clave:
- [requirements.txt](requirements.txt) — runtime
- [requirements-dev.txt](requirements-dev.txt) — desarrollo (añade `requests`)
- [package.json](package.json) — clientes JS de Supabase (`@supabase/ssr`, `@supabase/supabase-js`)

---

## 3. Arquitectura

El proyecto sigue una arquitectura **MVT (Model–View–Template)** clásica de Django, pero **sin modelos ORM propios**: toda la lógica de datos se delega a Supabase a través de una capa de servicios.

```
┌────────────────────────┐
│  Cliente (Navegador)   │
└──────────┬─────────────┘
           │ HTTP
┌──────────▼─────────────┐
│  Django (views.py)     │  ◄── Autenticación de sesión, validaciones,
│  + Templates           │      orquestación de flujos.
└──────────┬─────────────┘
           │
┌──────────▼─────────────┐
│  services/             │  ◄── Capa de servicios: encapsula llamadas
│  ├── auth_service      │      al SDK de Supabase.
│  ├── product_service   │
│  ├── purchase_service  │
│  └── supabase_client   │
└──────────┬─────────────┘
           │ HTTPS
┌──────────▼─────────────┐
│       Supabase         │
│  ├── Auth (usuarios)   │
│  ├── PostgreSQL        │
│  │   ├── profiles      │
│  │   ├── products      │
│  │   └── purchases     │
│  └── Storage (imágenes)│
└────────────────────────┘
```

### 3.1 Estructura de carpetas

```
metodologia/
├── manage.py                       # CLI de Django
├── db.sqlite3                      # DB interna de Django (sesiones, auth interno)
├── requirements.txt                # Dependencias de producción
├── requirements-dev.txt            # Dependencias de desarrollo
├── package.json                    # Dependencias JS (Supabase)
│
├── metodologia/                    # Proyecto Django principal
│   ├── settings.py                 # Configuración Django
│   ├── urls.py                     # Tabla de rutas
│   ├── views.py                    # Todas las vistas HTTP
│   ├── wsgi.py / asgi.py           # Entrypoints
│   └── __init__.py
│
├── services/                       # Capa de acceso a Supabase
│   ├── supabase_client.py          # Inicialización del cliente
│   ├── auth_service.py             # Registro / login
│   ├── product_service.py          # CRUD de productos + upload de imágenes
│   └── purchase_service.py         # Compras y perfiles
│
├── templates/                      # Plantillas Django (Jinja-like)
│   ├── base.html                   # Layout principal
│   ├── index.html                  # Home
│   ├── login.html / register.html  # Auth de usuarios
│   ├── admin_login.html            # Auth de admin
│   ├── admin_dashboard.html        # Panel admin
│   ├── admin_product_form.html     # Crear/editar producto (admin)
│   ├── carrito.html                # Vista de carrito
│   ├── cart_confirm.html           # Confirmación de compra
│   └── products/
│       ├── list.html
│       ├── create.html
│       └── edit.html
│
├── static/                         # Assets estáticos
│   ├── css/main.css
│   ├── js/                         # main.js, jquery, util, etc.
│   └── images/productos/           # Imágenes de productos
│
└── productos/                      # (Reservada para futura app modular)
```

---

## 4. Configuración

### 4.1 Variables de entorno

Se cargan desde un archivo `.env` en la raíz mediante `python-dotenv`. Ver [services/supabase_client.py:5-11](services/supabase_client.py#L5-L11) y [metodologia/settings.py:3-6](metodologia/settings.py#L3-L6).

| Variable | Obligatoria | Descripción |
|----------|:-----------:|-------------|
| `SUPABASE_URL` | Sí | URL del proyecto Supabase |
| `SUPABASE_KEY` | Sí | `anon` public key |
| `SUPABASE_SERVICE_ROLE_KEY` | No | Permite crear usuarios confirmados sin email (modo admin) |
| `SUPABASE_STORAGE_BUCKET` | No | Bucket de imágenes (default: `products`) |
| `SECRET_KEY` | Recomendada | Secret de Django (tiene fallback inseguro) |
| `ADMIN_USERNAME` | No | Usuario del panel admin (default: `admin`) |
| `ADMIN_PASSWORD` | No | Contraseña del panel admin (default: `admin123`) |

> **Aviso de seguridad:** el `ADMIN_PASSWORD` por defecto es débil y `DEBUG=True` está hardcodeado en [metodologia/settings.py:19](metodologia/settings.py#L19). Antes de un despliegue real ambos deben configurarse correctamente.

### 4.2 Hosts permitidos

Definidos en [metodologia/settings.py:21](metodologia/settings.py#L21):
- `metodologia-jv74.onrender.com`
- `127.0.0.1`
- `localhost`

---

## 5. Modelo de datos (Supabase)

Las tablas viven en PostgreSQL gestionado por Supabase. No hay migraciones de Django para ellas; se administran desde el panel de Supabase.

### 5.1 `profiles`
| Campo | Tipo | Notas |
|-------|------|-------|
| `id` | bigint (PK) | Autogenerado |
| `email` | text | Único, espejo de `auth.users.email` |
| `first_name` | text | |
| `last_name` | text | |
| `tel` | text | Opcional |

### 5.2 `products`
| Campo | Tipo | Notas |
|-------|------|-------|
| `id` | bigint (PK) | |
| `name` | text | |
| `description` | text | |
| `price` | numeric | ≥ 0 |
| `stock` | int | ≥ 0 |
| `image` | text | URL pública (Storage o externa) |

### 5.3 `purchases`
| Campo | Tipo | Notas |
|-------|------|-------|
| `id` | bigint (PK) | |
| `user_id` | bigint (FK → profiles.id) | |
| `product_id` | bigint (FK → products.id) | |
| `amount` | int | Cantidad comprada |
| `status` | text | Estado de la compra |
| `created_at` | timestamptz | |

### 5.4 RPC `finish_purchase`
Función almacenada en PostgreSQL invocada vía `client.rpc("finish_purchase", ...)` en [services/purchase_service.py:19-24](services/purchase_service.py#L19-L24). Recibe:
- `input_user_id`
- `input_product_id`
- `input_amount`

Responsable de descontar stock, registrar la compra y validar disponibilidad de forma transaccional.

### 5.5 Storage
Bucket `products` (configurable). Las imágenes subidas se guardan bajo `products/<slug>-<uuid>.<ext>`. Tipos permitidos: JPG, PNG, WEBP, GIF. Ver [services/product_service.py:11-42](services/product_service.py#L11-L42).

---

## 6. Rutas y vistas

Todas las rutas están declaradas en [metodologia/urls.py](metodologia/urls.py) y las vistas en [metodologia/views.py](metodologia/views.py).

### 6.1 Públicas

| Método | Ruta | Vista | Descripción |
|--------|------|-------|-------------|
| GET | `/` | `home` | Home con listado de productos |
| GET/POST | `/register/` | `register` | Registro de usuarios |
| GET/POST | `/login/` | `login` | Login de usuarios |
| GET | `/logout/` | `logout` | Cierra sesión y limpia carrito |
| GET | `/products/` | `products_list` | Listado público de productos |

### 6.2 Carrito (requieren sesión de usuario)

Decorador: `@require_user` ([metodologia/views.py:110-116](metodologia/views.py#L110-L116))

| Método | Ruta | Vista | Descripción |
|--------|------|-------|-------------|
| GET | `/cart/` | `cart_view` | Renderiza el carrito |
| GET | `/cart/data/` | `cart_data` | JSON con ítems y total |
| POST | `/cart/add/<id>/` | `add_to_cart` | Agrega producto (soporta AJAX) |
| POST | `/cart/update/<id>/` | `update_cart_item` | Cambia cantidad |
| POST | `/cart/remove/<id>/` | `remove_cart_item` | Quita un producto |
| GET | `/cart/confirm/` | `checkout_confirm` | Pantalla de confirmación |
| POST | `/cart/checkout/` | `checkout` | Ejecuta la compra (RPC) |

### 6.3 Administración (requieren admin autenticado)

Decorador: `@require_admin` ([metodologia/views.py:101-107](metodologia/views.py#L101-L107))

| Método | Ruta | Vista | Descripción |
|--------|------|-------|-------------|
| GET/POST | `/admin/login/` | `admin_login` | Login con credenciales fijas en env |
| GET | `/admin/` | `admin_dashboard` | Productos + compras recientes |
| GET/POST | `/admin/product/create/` | `admin_product_create` | Crear producto |
| GET/POST | `/admin/product/edit/<id>/` | `admin_product_edit` | Editar producto |
| POST | `/admin/product/delete/<id>/` | `admin_product_delete` | Eliminar producto |
| GET | `/admin/purchases/data/` | `admin_purchases_data` | JSON con compras |
| GET | `/admin/logout/` | `admin_logout` | Cierra sesión admin |

> Las rutas `/products/create/`, `/products/edit/<id>/` y `/products/delete/<id>/` son legacy: usan `@require_admin` y conviven con las nuevas rutas `/admin/product/...`.

---

## 7. Flujos principales

### 7.1 Registro
1. Usuario completa `register.html`.
2. La vista valida nombre, email y teléfono ([metodologia/views.py:36-49](metodologia/views.py#L36-L49)).
3. Si hay `SUPABASE_SERVICE_ROLE_KEY`, se llama a `auth.admin.create_user` con `email_confirm=True` (auto-confirmado). Si no, se usa `sign_up` regular ([services/auth_service.py:19-31](services/auth_service.py#L19-L31)).
4. Se inserta el perfil en `profiles`.
5. Se hace login automático y se guarda `user_email` y `user_token` en sesión.

### 7.2 Login
1. Validación de email no vacío y bien formado.
2. `supabase_auth.auth.sign_in_with_password` → devuelve `user` + `session`.
3. Se persisten `user_email` y `user_token` (JWT) en la sesión Django.

### 7.3 Carrito
- Almacenado en `request.session["cart"]` como `{ "<product_id>": cantidad }`.
- `get_cart_payload` ([metodologia/views.py:134-168](metodologia/views.py#L134-L168)) reconstruye el detalle leyendo cada producto de Supabase.

### 7.4 Checkout
1. El usuario confirma en `/cart/confirm/`.
2. POST a `/cart/checkout/` ([metodologia/views.py:650-698](metodologia/views.py#L650-L698)):
   - Lee perfil por email.
   - Crea un cliente de Supabase **autenticado con el JWT del usuario** (`get_user_supabase`) para que las políticas RLS apliquen.
   - Por cada producto del carrito invoca el RPC `finish_purchase` (descuenta stock + crea fila en `purchases`).
   - Si falla un ítem, se preservan en el carrito los aún no procesados y se reporta el error.
3. Al éxito vacía el carrito y marca `checkout_success=True`.

### 7.5 Administración de productos
- Crear/Editar usan `build_product_data` ([metodologia/views.py:68-98](metodologia/views.py#L68-L98)) que valida campos, sube la imagen a Storage si vino por archivo, o usa una URL externa.
- `upload_image` retorna la URL pública del objeto en Supabase Storage.

---

## 8. Autenticación y autorización

| Tipo | Mecanismo | Sesión Django |
|------|-----------|---------------|
| Usuario final | Supabase Auth (email + password) | `user_email`, `user_token` |
| Administrador | Credenciales fijas en env (`ADMIN_USERNAME` / `ADMIN_PASSWORD`) | `admin_authenticated=True` |

Los decoradores `require_user` y `require_admin` redirigen al login correspondiente cuando la sesión no tiene la clave esperada.

> **CSRF:** todas las vistas usan el middleware CSRF estándar. Solo `admin_login` está marcada con `@csrf_exempt` ([metodologia/views.py:291](metodologia/views.py#L291)).

---

## 9. Frontend

- **Plantilla base:** [templates/base.html](templates/base.html), reutilizada por todas las vistas vía `{% extends %}`.
- **Tema visual:** HTML5UP **Editorial** (CSS en `static/css/main.css`, JS de jQuery en `static/js/`).
- **Imágenes de catálogo:** servidas desde `static/images/productos/` o desde Supabase Storage.
- El carrito refresca su contenido por AJAX (`/cart/data/`) y soporta agregar productos con `XMLHttpRequest`.

---

## 10. Tests

Existen dos tipos de prueba:

### 10.1 Tests unitarios (Django TestCase)
[test_auth_views.py](test_auth_views.py) — mockea los servicios Supabase y verifica:
- Que un email inválido en `/register/` no llame a `create_confirmed_user`.
- Que un registro válido redirige a `/` y crea el perfil.
- Que un email inválido en `/login/` no llame a `login_user`.

Ejecutar con:
```bash
python manage.py test
```

### 10.2 Smoke test HTTP
[test_register.py](test_register.py) — script independiente con `requests` que extrae el token CSRF, hace POST real al servidor en `127.0.0.1:8000` y reporta el resultado. Requiere el servidor corriendo.

```bash
python test_register.py
```

---

## 11. Puesta en marcha local

```bash
# 1. Clonar y entrar al proyecto
cd metodologia

# 2. Crear y activar un virtualenv (Windows / PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Instalar dependencias
pip install -r requirements-dev.txt

# 4. Crear archivo .env con al menos:
#    SUPABASE_URL=...
#    SUPABASE_KEY=...
#    SUPABASE_SERVICE_ROLE_KEY=... (opcional pero recomendado)
#    SECRET_KEY=...
#    ADMIN_USERNAME=...
#    ADMIN_PASSWORD=...

# 5. Aplicar migraciones internas de Django (sesiones, auth interno)
python manage.py migrate

# 6. Levantar el servidor
python manage.py runserver
```

La aplicación queda disponible en `http://127.0.0.1:8000/` y el panel admin en `http://127.0.0.1:8000/admin/login/`.

---

## 12. Despliegue

El proyecto está desplegado en **Render** bajo el dominio `metodologia-jv74.onrender.com`. Para producción:

- `gunicorn` como servidor WSGI (`gunicorn metodologia.wsgi:application`).
- `whitenoise` sirve los estáticos (`STATIC_ROOT = BASE_DIR / 'staticfiles'`).
- Variables sensibles cargadas como **Environment Variables** del servicio de Render.
- Antes del deploy: `python manage.py collectstatic --noinput`.

> Pendiente para producción real: poner `DEBUG=False`, rotar el `SECRET_KEY`, y configurar credenciales admin fuertes.

---

## 13. Decisiones de diseño relevantes

- **Sin modelos ORM de Django para datos de negocio.** Se eligió mantener la base de datos como verdad central en Supabase, accedida desde Python mediante el SDK oficial. Django se conserva por su sistema de sesiones, templates, middleware CSRF y por el ecosistema de despliegue.
- **Capa `services/`.** Aísla las vistas del SDK de Supabase: las pruebas mockean estos módulos en lugar de la red.
- **Doble cliente Supabase** ([services/supabase_client.py:19-26](services/supabase_client.py#L19-L26)):
  - `supabase` con `service_role` (o `anon` como fallback) para operaciones administrativas.
  - `supabase_auth` siempre con `anon` para flujos públicos de login/registro.
  - `get_user_supabase(token)` para invocar RPCs con la identidad del usuario (RLS).
- **Stock transaccional vía RPC.** El descuento de stock se ejecuta del lado de la base con `finish_purchase` para evitar carreras entre carritos simultáneos.
- **Admin con credenciales fijas.** Pensado para un TP didáctico, no para producción real. Si se quiere escalar conviene migrar a Supabase Auth con un rol `admin`.

---

## 14. Glosario rápido

- **RLS (Row Level Security):** políticas de PostgreSQL/Supabase que filtran filas por identidad del JWT.
- **RPC:** función almacenada en PostgreSQL invocable como endpoint REST por Supabase.
- **Storage:** servicio de archivos de Supabase (similar a S3) usado para imágenes de productos.
- **WhiteNoise:** middleware que sirve archivos estáticos directamente desde la app WSGI.

---

## 15. Próximos pasos sugeridos

1. Mover las credenciales del admin a Supabase Auth con un claim/rol específico.
2. Cubrir con tests las rutas del carrito y checkout (RPC mockeado).
3. Configurar `DEBUG=False` y `ALLOWED_HOSTS` dinámicos por entorno.
4. Añadir migraciones documentadas (SQL) para `profiles`, `products`, `purchases` y el RPC `finish_purchase` dentro del repo (`/migrations/*.sql`).
5. Integrar CI (GitHub Actions) que corra `python manage.py test` en cada PR.