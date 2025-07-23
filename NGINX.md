# NGINX as an API Gateway

## Overview
NGINX is a high-performance web server and reverse proxy server that can be used as an API Gateway. It acts as a single entry point for multiple backend services, handling tasks such as routing, load balancing, and security. This configuration is particularly useful for microservices architectures, where multiple services need to be exposed through a unified interface.

In this guide, we will:
1. Explain the provided NGINX configuration.
2. Provide step-by-step instructions to install and set up NGINX.
3. Show the complete configuration for the AgendaGol microservices.

---

## Configuration Explanation

The provided NGINX configuration routes requests to different backend services based on the URL path. Here's a breakdown:

1. **Common Configuration**:
   - `proxy_set_header Host $host`: Preserves the original host header
   - `proxy_set_header X-Real-IP $remote_addr`: Forwards the real client IP
   - `proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for`: Adds client IP to forwarded headers
   - `proxy_set_header Authorization $http_authorization`: Ensures the `Authorization` header is forwarded for authentication purposes

2. **Service Routing**:
   - Each `location` block defines a route for a specific service:
     - `/auth`: Routes to the authentication service on `localhost:8000`
     - `/roles`: Routes to the roles service on `localhost:8001`
     - `/fields`: Routes to the fields service on `localhost:8002`
     - `/reservations`: Routes to the reservations service on `localhost:8003`
     - `/dashboard`: Routes to the dashboard service on `localhost:8004`
   - Each service supports CORS (Cross-Origin Resource Sharing) by adding headers like `Access-Control-Allow-Origin`
   - URL rewriting removes the service prefix before forwarding to backend

3. **CORS Support**:
   - Handles preflight OPTIONS requests
   - Allows all origins (`*`) for development
   - Supports common HTTP methods (GET, POST, PUT, DELETE, OPTIONS)
   - Forwards Authorization and Content-Type headers

4. **Error Handling**:
   - Custom error pages for `404` (Not Found) and `500` (Internal Server Error) return JSON responses
   - Maintains API consistency even for errors

---

## Complete NGINX Configuration

Here's the complete configuration file for the AgendaGol microservices:

```nginx
server {
    listen 80;
    server_name ip_host;
    
    # Configuración común
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header Authorization $http_authorization;

    # Servicio de Autenticación (/auth/*)
    location /auth {
        if ($request_method = 'OPTIONS') {
            return 204;
        }

        proxy_pass http://localhost:8000;
        rewrite ^/auth/(.*) /$1 break;

        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type' always;
    }

    # Servicio de Roles
    location /roles {
        if ($request_method = 'OPTIONS') {
            return 204;
        }

        proxy_pass http://localhost:8001;
        rewrite ^/roles/(.*) /$1 break;

        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type' always;
    }

    # Servicio de Canchas
    location /fields {
        if ($request_method = 'OPTIONS') {
            return 204;
        }

        proxy_pass http://localhost:8002;
        rewrite ^/fields/(.*) /$1 break;

        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type' always;
    }

    # Servicio de Reservas
    location /reservations {
        if ($request_method = 'OPTIONS') {
            return 204;
        }

        proxy_pass http://localhost:8003;
        rewrite ^/reservations/(.*) /$1 break;

        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type' always;
    }

    # Servicio de Dashboard
    location /dashboard {
        if ($request_method = 'OPTIONS') {
            return 204;
        }

        proxy_pass http://localhost:8004;
        rewrite ^/dashboard/(.*) /$1 break;

        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type' always;
    }

    # Manejo de errores
    error_page 404 /404.json;
    location = /404.json {
        internal;
        default_type application/json;
        return 404 '{"error": "Not found", "status": 404}';
    }

    error_page 500 502 503 504 /50x.json;
    location = /50x.json {
        internal;
        default_type application/json;
        return 500 '{"error": "Internal server error", "status": 500}';
    }
}
```

---

## Installation and Setup

Follow these steps to install and configure NGINX:

### 1. Install NGINX
On a Linux-based system (e.g., Ubuntu):
```bash
sudo apt update
sudo apt install nginx
```

### 2. Start and Enable NGINX
```bash
# Start NGINX service
sudo systemctl start nginx

# Enable NGINX to start automatically on boot
sudo systemctl enable nginx

# Check NGINX status
sudo systemctl status nginx
```

### 3. Configure NGINX

#### Option A: Replace the default configuration
```bash
# Backup the original configuration
sudo cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.backup

# Edit the configuration file
sudo nano /etc/nginx/sites-available/default
```

Copy and paste the complete configuration shown above into the file.

#### Option B: Create a new site configuration
```bash
# Create a new configuration file
sudo nano /etc/nginx/sites-available/agendagol

# Create symbolic link to enable the site
sudo ln -s /etc/nginx/sites-available/agendagol /etc/nginx/sites-enabled/

# Remove default site (optional)
sudo rm /etc/nginx/sites-enabled/default
```

### 4. Test Configuration and Restart
```bash
# Test NGINX configuration for syntax errors
sudo nginx -t

# If test passes, reload NGINX
sudo systemctl reload nginx

# Or restart NGINX
sudo systemctl restart nginx
```

### 5. Configure Firewall (if needed)
```bash
# Allow HTTP traffic
sudo ufw allow 'Nginx HTTP'

# Or allow both HTTP and HTTPS
sudo ufw allow 'Nginx Full'

# Check firewall status
sudo ufw status
```

### 6. Verify Installation
```bash
# Check if NGINX is running
curl http://localhost

# Check if the API Gateway is working
curl http://ip_host/auth/health
curl http://ip_host/fields/
```

---

## Service Architecture

With this NGINX configuration, your microservices architecture works as follows:

```
Client Request → NGINX (Port 80) → Backend Services

http://ip_host/auth/*         → localhost:8000 (Auth Service)
http://ip_host/roles/*        → localhost:8001 (Roles Service)
http://ip_host/fields/*       → localhost:8002 (Fields Service)
http://ip_host/reservations/* → localhost:8003 (Reservations Service)
http://ip_host/dashboard/*    → localhost:8004 (Dashboard Service)
```

---

## Benefits of Using NGINX as API Gateway

1. **Single Entry Point**: All services accessible through one domain/IP
2. **Load Balancing**: Can distribute requests across multiple service instances
3. **SSL Termination**: Handle HTTPS at the gateway level
4. **CORS Management**: Centralized CORS policy management
5. **Rate Limiting**: Can implement rate limiting at the gateway level
6. **Caching**: Can cache responses to improve performance
7. **Security**: Can implement authentication and authorization at the gateway level

---

## Troubleshooting

### Common Issues:

1. **503 Service Unavailable**: Backend services are not running
   ```bash
   # Check if services are running on correct ports
   netstat -tlnp | grep :800[0-4]
   ```

2. **CORS Errors**: Check browser developer tools and NGINX logs
   ```bash
   # Check NGINX error logs
   sudo tail -f /var/log/nginx/error.log
   ```

3. **Configuration Errors**: 
   ```bash
   # Always test configuration before reloading
   sudo nginx -t
   ```

### Logs Location:
- Access logs: `/var/log/nginx/access.log`
- Error logs: `/var/log/nginx/error.log`