-- Script para crear todas las bases de datos necesarias (solo si no existen)
SELECT 'CREATE DATABASE auth_db' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'auth_db')\gexec
SELECT 'CREATE DATABASE roles_db' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'roles_db')\gexec
SELECT 'CREATE DATABASE fields_db' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'fields_db')\gexec
SELECT 'CREATE DATABASE reservations_db' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'reservations_db')\gexec
SELECT 'CREATE DATABASE dashboard_db' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'dashboard_db')\gexec

-- Otorgar permisos al usuario postgres
GRANT ALL PRIVILEGES ON DATABASE auth_db TO postgres;
GRANT ALL PRIVILEGES ON DATABASE roles_db TO postgres;
GRANT ALL PRIVILEGES ON DATABASE fields_db TO postgres;
GRANT ALL PRIVILEGES ON DATABASE reservations_db TO postgres;
GRANT ALL PRIVILEGES ON DATABASE dashboard_db TO postgres;