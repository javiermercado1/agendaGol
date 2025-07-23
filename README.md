# 🏗️ Arquitectura de Microservicios

## Descripción General
- **5 servicios independientes** con sus propias bases de datos.  
- Comunicación vía **REST APIs** entre servicios.  
- **Docker Compose** para deployment completo.  
- Health checks y manejo de dependencias.  

---

## Servicios

### 🔐 Auth Service (Puerto 8000)
- Registro y login de usuarios.  
- Recuperación de contraseña.  
- Gestión de perfiles.  
- Verificación de tokens.  
- Estadísticas de usuarios.  

### 👥 Roles Service (Puerto 8001)
- CRUD completo de roles y permisos.  
- Asignación de permisos a usuarios.  
- Validación de permisos.  
- Roles por defecto: **admin** y **user**.  

### 🏟️ Fields Service (Puerto 8002)
- CRUD de canchas (solo Admin).  
- Información completa: nombre, ubicación, capacidad, precio.  
- Horarios configurables (10 AM - 10 PM por defecto).  
- Verificación de disponibilidad.  
- Validación de permisos.  

### 📅 Reservations Service (Puerto 8003)
- Crear reservas con validaciones completas.  
- Duración: **1 o 2 horas**.  
- Estados: **Confirmada** y **Cancelada**.  
- Máximo **30 días de anticipación**.  
- Prevención de conflictos de horario.  
- Edición y cancelación de reservas.  
- Sistema de emails automático.  
- Estadísticas de reservas.  

### 📊 Admin Dashboard (Puerto 8004)
- Estadísticas en tiempo real.  
- Últimas reservas confirmadas y canceladas.  
- Conteo de usuarios, canchas y reservas.  
- Estadísticas detalladas por cancha.  
- Ingresos diarios.  
- Estado de salud de todos los servicios.  
- Vista de usuarios con filtros.  

---

## 📧 Sistema de Notificaciones
- Email de confirmación al crear reserva.  
- Email de notificación al cancelar.  
- Configuración SMTP completa.  
- Templates HTML incluidos.  

---

## 🛡️ Validaciones y Seguridad
- Validación de permisos entre servicios.  
- Tokens JWT con información completa.  
- Validaciones de horarios y disponibilidad.  
- Prevención de reservas duplicadas.  
- Soft delete para canchas.  

---

## 🗄️ Base de Datos
- **5 bases de datos independientes**:  
    - `auth_db`  
    - `roles_db`  
    - `fields_db`  
    - `reservations_db`  
    - `dashboard_db`  
- Modelos completos con relaciones.  
- Inicialización automática.  
- Datos de ejemplo incluidos.  

---

## 🐳 Instalación de Docker y Docker Compose

### Requisitos Previos
- Sistema operativo compatible (Linux, macOS, Windows).
- Acceso a una terminal con permisos de administrador.

### Instalación de Docker
1. **Linux**:  
   ```bash
   sudo apt update
   sudo apt install -y docker.io
   sudo systemctl start docker
   sudo systemctl enable docker
   ```
2. **macOS**:  
   Descarga e instala Docker Desktop desde [Docker para macOS](https://www.docker.com/products/docker-desktop).
3. **Windows**:  
   Descarga e instala Docker Desktop desde [Docker para Windows](https://www.docker.com/products/docker-desktop).

### Instalación de Docker Compose
1. **Linux**:  
   ```bash
   sudo curl -L "https://github.com/docker/compose/releases/download/$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep -oP '"tag_name": "\K(.*)(?=")')/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```
2. **macOS y Windows**:  
   Docker Compose viene incluido con Docker Desktop.

### Verificación de Instalación
Ejecuta los siguientes comandos para verificar que Docker y Docker Compose están instalados correctamente:
```bash
docker --version
docker-compose --version
```

### Configuración Adicional
- Asegúrate de que tu usuario pertenece al grupo `docker` para evitar usar `sudo`:
  ```bash
  sudo usermod -aG docker $USER
  ```
  Luego, reinicia tu sesión.

---

## 🚀 Despliegue con Docker Compose
1. Clona el repositorio:
   ```bash
   git clone https://github.com/javiermercado1/agendaGol.git
   cd agendagol
   ```
2. Construye y levanta los servicios:
   ```bash
   docker-compose up --build
   ```
3. Accede a los servicios en los puertos especificados.

---

Para la configuración de NGINX, consulta el archivo [`NGINX.md`](NGINX.md).  

Para la información del sistema, consulta el archivo [`README_SISTEMA.md`](README_SISTEMA.md).
