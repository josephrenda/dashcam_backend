#!/bin/bash

# SSL Setup Script for Dashcam Backend
# This script installs certbot and generates Let's Encrypt SSL certificates

set -e

echo "=== SSL Setup for Dashcam Backend ==="

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root or with sudo"
    exit 1
fi

# Install certbot
echo "Installing certbot..."
apt-get update
apt-get install -y certbot python3-certbot-nginx

# Get domain name
read -p "Enter your domain name (e.g., api.example.com): " DOMAIN

# Get email for Let's Encrypt
read -p "Enter your email address for Let's Encrypt notifications: " EMAIL

# Stop nginx if running
echo "Stopping nginx..."
docker-compose -f docker-compose.prod.yml stop nginx || true

# Generate certificate
echo "Generating SSL certificate..."
certbot certonly --standalone \
    --preferred-challenges http \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    -d "$DOMAIN"

# Update nginx configuration for SSL
echo "Updating nginx configuration..."
cat > docker/nginx/nginx.conf << EOF
upstream api {
    server api:8000;
}

server {
    listen 80;
    server_name $DOMAIN;
    
    location / {
        return 301 https://\$host\$request_uri;
    }
}

server {
    listen 443 ssl;
    server_name $DOMAIN;

    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    client_max_body_size 500M;

    location / {
        proxy_pass http://api;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;

        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
        proxy_read_timeout 600s;
    }
}
EOF

# Update docker-compose to mount certificates
echo "Updating docker-compose configuration..."
# Note: You'll need to manually add the volume mount to docker-compose.prod.yml:
# volumes:
#   - /etc/letsencrypt:/etc/letsencrypt:ro

echo ""
echo "=== SSL Setup Complete ==="
echo ""
echo "IMPORTANT: Add the following volume mount to nginx service in docker-compose.prod.yml:"
echo "  volumes:"
echo "    - ./docker/nginx/nginx.conf:/etc/nginx/conf.d/default.conf"
echo "    - /etc/letsencrypt:/etc/letsencrypt:ro"
echo ""
echo "Then restart nginx:"
echo "  docker-compose -f docker-compose.prod.yml up -d nginx"
echo ""
echo "To set up auto-renewal, add this to crontab (crontab -e):"
echo "0 0 * * * certbot renew --quiet && docker-compose -f /path/to/docker-compose.prod.yml restart nginx"
