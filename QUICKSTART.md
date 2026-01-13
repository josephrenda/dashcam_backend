# Quick Start Guide

Get the Dashcam Backend up and running in 5 minutes!

## Prerequisites

- Docker and Docker Compose installed
- Git installed
- Port 80 and 3306 available

## Step 1: Clone the Repository

```bash
git clone https://github.com/josephrendacec/dashcam_backend.git
cd dashcam_backend
```

## Step 2: Set Up Environment

```bash
cp .env.example .env
```

**Important**: Edit `.env` and change `API_SECRET_KEY` to a secure random string:

```bash
# Generate a secure secret key (Linux/Mac)
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Step 3: Start All Services

```bash
docker-compose up -d
```

This will start:
- ✅ MySQL database
- ✅ Redis cache
- ✅ FastAPI backend
- ✅ Celery worker
- ✅ Nginx reverse proxy
- ✅ OSRM routing engine

## Step 4: Run Database Migrations

```bash
docker-compose exec api alembic upgrade head
```

## Step 5: Verify Installation

Check that all services are running:

```bash
docker-compose ps
```

Test the API:

```bash
curl http://localhost/health
```

Expected response: `{"status":"healthy"}`

## Step 6: Access API Documentation

Open your browser and visit:
- **Swagger UI**: http://localhost/docs
- **ReDoc**: http://localhost/redoc

## First API Call - Register a User

```bash
curl -X POST http://localhost/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "SecurePassword123!"
  }'
```

## Login and Get Token

```bash
curl -X POST http://localhost/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePassword123!"
  }'
```

Save the `access_token` from the response!

## Report Your First Incident

```bash
# Replace YOUR_ACCESS_TOKEN with the token from login
curl -X POST http://localhost/api/v1/incidents/report \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "video=@path/to/video.mp4" \
  -F "type=crash" \
  -F "latitude=37.7749" \
  -F "longitude=-122.4194" \
  -F "timestamp=2024-01-13T10:30:00Z" \
  -F "description=Test incident"
```

## View Logs

```bash
# API logs
docker-compose logs -f api

# Celery worker logs
docker-compose logs -f celery_worker

# All logs
docker-compose logs -f
```

## Stop Services

```bash
docker-compose down
```

## Troubleshooting

### Port Already in Use

If port 80 or 3306 is already in use, edit `docker-compose.yml`:

```yaml
services:
  nginx:
    ports:
      - "8080:80"  # Change 80 to 8080
  
  mysql:
    ports:
      - "3307:3306"  # Change 3306 to 3307
```

### Database Connection Failed

Wait a few seconds for MySQL to fully start:

```bash
docker-compose logs mysql
```

Look for: "ready for connections"

### Video Upload Fails

Check video storage permissions:

```bash
docker-compose exec api mkdir -p /var/data/videos
docker-compose exec api chmod 777 /var/data/videos
```

## Next Steps

1. Read the full [README.md](README.md) for detailed documentation
2. Check [API_EXAMPLES.md](API_EXAMPLES.md) for more API examples
3. Explore the interactive API docs at http://localhost/docs
4. Set up SSL for production using `scripts/setup-ssl.sh`
5. Download OSRM map data using `scripts/download-osrm-data.sh`

## Production Deployment

For production deployment, use:

```bash
docker-compose -f docker-compose.prod.yml up -d
```

Don't forget to:
- ✅ Set strong passwords in `.env`
- ✅ Set `DEBUG=False`
- ✅ Set `ENVIRONMENT=production`
- ✅ Configure SSL certificates
- ✅ Set up firewall rules
- ✅ Configure backup strategy

## Need Help?

- Check the [README.md](README.md) for full documentation
- Review [API_EXAMPLES.md](API_EXAMPLES.md) for usage examples
- Open an issue on GitHub for bugs or questions

---

**Happy Coding! 🚗📹**
