-- Script para crear todas las bases de datos necesarias
CREATE DATABASE auth_db;
CREATE DATABASE roles_db;
CREATE DATABASE fields_db;
CREATE DATABASE reservations_db;
CREATE DATABASE dashboard_db;

-- Otorgar permisos al usuario postgres
GRANT ALL PRIVILEGES ON DATABASE auth_db TO postgres;
GRANT ALL PRIVILEGES ON DATABASE roles_db TO postgres;
GRANT ALL PRIVILEGES ON DATABASE fields_db TO postgres;
GRANT ALL PRIVILEGES ON DATABASE reservations_db TO postgres;
GRANT ALL PRIVILEGES ON DATABASE dashboard_db TO postgres;
