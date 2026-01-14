# 🏗️ AgendaGol - Microservicios

Este proyecto es un sistema de gestión de canchas y reservas basado en una arquitectura de microservicios.

---

## 🚀 Cómo Correr el Proyecto (Despliegue Rápido)

Para levantar todos los servicios automáticamente con un solo comando:

### **En Windows (PowerShell):**
```powershell
.\make init
```

### **En Windows (CMD) / Linux / Mac:**
```bash
make init
```

> [!TIP]
> Si no tienes `make` instalado en Linux/Mac, utiliza directamente: `docker-compose up --build`.

---

## 🛠️ Comandos de Gestión

- `make init`: Construye y levanta todo (recomendado la primera vez).
- `make start`: Inicia los servicios en segundo plano.
- `make stop`: Detiene todos los servicios.
- `make logs`: Ver logs en tiempo real.
- `make status`: Ver estado de los contenedores.
- `make clean`: Borra contenedores y bases de datos locales.

---

## � Guía de Integración para Frontend

### 🔑 Autenticación (JWT)
La mayoría de los servicios protegidos requieren un token **JSON Web Token (JWT)**.
1. **Registro**: Crea un usuario en `POST :8000/auth/register`.
2. **Login**: Obtén el `access_token` en `POST :8000/auth/login`.
3. **Uso**: Incluye el token en el header de tus peticiones:
   `Authorization: Bearer <tu_token>`

### 🌐 CORS (Cross-Origin Resource Sharing)
Todos los microservicios tienen CORS habilitado con `allow_origins=["*"]`, por lo que puedes consumirlos desde Next.js sin problemas de bloqueo.

### 🚦 Flujo Principal de Reservas
Para implementar una reserva completa, el flujo sugerido es:
1. **Listar Canchas**: `GET :8002/fields/`.
2. **Verificar Disponibilidad**: `GET :8002/fields/{id}/availability?date=YYYY-MM-DD`.
3. **Crear Reserva**: `POST :8003/reservations/` (Requiere login).

### 🚩 Reglas de Negocio a Considerar
- Las reservas solo pueden ser de **1 o 2 horas**.
- No se pueden hacer reservas con más de **30 días de anticipación**.
- El horario de atención por defecto es de **10:00 AM a 10:00 PM**.

### 🧪 Colección de Postman
En la raíz del proyecto encontrarás `postman_collection_full.json`. Puedes importarla en Postman para ver ejemplos detallados de los cuerpos (JSON) que espera cada endpoint.

---

## �📡 Detalles de los Endpoints

El sistema se divide en 5 microservicios principales:

### 🔐 Auth Service (Puerto 8000)
*Base URL: `http://localhost:8000/auth`*
- `POST /register`: Registro de nuevos usuarios.
- `POST /login`: Inicio de sesión (retorna JWT).
- `GET /me`: Información del usuario actual.
- `GET /verify`: Verificación de validez de token.

### 👥 Roles Service (Puerto 8001)
*Base URL: `http://localhost:8001`*
- `GET /roles`: Listar roles disponibles.
- `POST /validate-permission`: Verificar si un usuario tiene un permiso específico.
- `POST /users/{id}/assign-role`: Asignar roles a usuarios.

### 🏟️ Fields Service (Puerto 8002)
*Base URL: `http://localhost:8002/fields`*
- `GET /`: Listar todas las canchas.
- `POST /`: Crear nueva cancha (Admin).
- `GET /{id}/availability`: Ver horarios disponibles para una fecha.

### 📅 Reservations Service (Puerto 8003)
*Base URL: `http://localhost:8003/reservations`*
- `GET /`: Listar todas las reservas.
- `POST /`: Crear una reserva (1 o 2 horas).
- `GET /my`: Ver reservas del usuario autenticado.
- `POST /{id}/cancel`: Cancelar una reserva existente.

### 📊 Admin Dashboard (Puerto 8004)
*Base URL: `http://localhost:8004/dashboard`*
- `GET /stats`: Resumen global de usuarios, canchas e ingresos.
- `GET /health-check`: Estado de salud de todos los microservicios.
- `GET /fields/stats`: Estadísticas de uso por cada cancha.

---