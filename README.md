# Dashcam Backend

A comprehensive backend API for dashcam incident reporting and video processing with machine learning capabilities.

## Features

- **User Authentication**: JWT-based authentication with access and refresh tokens
- **Incident Reporting**: Upload and manage dashcam incident videos
- **Video Processing**: Automatic video processing with ML models
- **Vehicle Detection**: YOLO-based vehicle detection in video frames
- **License Plate Recognition**: OCR-based license plate detection and reading
- **Nearby Incidents**: Query incidents by location and time
- **Background Processing**: Celery-based asynchronous video processing
- **RESTful API**: FastAPI with automatic OpenAPI documentation
- **Docker Support**: Complete Docker and Docker Compose configuration

## Technology Stack

- **Framework**: FastAPI 0.109.0
- **Database**: MySQL 8.0 with SQLAlchemy ORM
- **Caching**: Redis 7
- **Task Queue**: Celery 5.3.6
- **ML Models**: YOLOv8 (Ultralytics) for vehicle detection
- **OCR**: EasyOCR for license plate recognition
- **Video Processing**: OpenCV
- **Authentication**: JWT with python-jose
- **Password Hashing**: bcrypt via passlib
- **Routing**: OSRM for route optimization
- **Web Server**: Nginx (reverse proxy)

## Project Structure

```
dashcam_backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   ├── celery_app.py              # Celery configuration
│   ├── api/
│   │   ├── dependencies.py        # API dependencies (auth, etc.)
│   │   └── v1/
│   │       ├── router.py          # API v1 router
│   │       └── endpoints/
│   │           ├── auth.py        # Authentication endpoints
│   │           ├── incidents.py   # Incident management endpoints
│   │           └── users.py       # User management endpoints
│   ├── core/
│   │   ├── config.py              # Configuration management
│   │   ├── database.py            # Database setup
│   │   └── security.py            # Security utilities
│   ├── models/
│   │   ├── user.py                # User database model
│   │   ├── incident.py            # Incident database model
│   │   └── vehicle.py             # Vehicle detection models
│   ├── schemas/
│   │   ├── auth.py                # Authentication schemas
│   │   ├── incident.py            # Incident schemas
│   │   └── user.py                # User schemas
│   ├── services/
│   │   ├── video_processor.py    # Video processing service
│   │   ├── ml_detector.py        # ML detection service
│   │   └── ocr_service.py        # OCR service
│   └── tasks/
│       └── celery_tasks.py        # Background tasks
├── alembic/                        # Database migrations
├── docker/                         # Docker configurations
├── scripts/                        # Utility scripts
├── tests/                          # Test suite
├── .env.example                    # Environment variables template
├── docker-compose.yml              # Development compose file
├── docker-compose.prod.yml         # Production compose file
└── requirements.txt                # Python dependencies
```

## Setup Instructions

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/josephrendacec/dashcam_backend.git
cd dashcam_backend
```

### 2. Environment Configuration

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit the `.env` file and update the following:
- `API_SECRET_KEY`: Generate a strong secret key
- `MYSQL_ROOT_PASSWORD`: Set a secure root password
- `MYSQL_PASSWORD`: Set a secure user password
- `ENVIRONMENT`: Set to `production` for production deployment
- `DEBUG`: Set to `False` for production

### 3. Start Services with Docker Compose

For development:

```bash
docker-compose up -d
```

For production:

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 4. Run Database Migrations

```bash
# Create initial migration
docker-compose exec api alembic revision --autogenerate -m "Initial migration"

# Apply migrations
docker-compose exec api alembic upgrade head
```

### 5. Download OSRM Map Data (Optional)

For route optimization features:

```bash
chmod +x scripts/download-osrm-data.sh
./scripts/download-osrm-data.sh
```

### 6. Setup SSL (Production Only)

```bash
sudo chmod +x scripts/setup-ssl.sh
sudo ./scripts/setup-ssl.sh
```

## API Documentation

Once the application is running, access the interactive API documentation:

- **Swagger UI**: http://localhost/docs
- **ReDoc**: http://localhost/redoc

## API Endpoints

### Authentication

- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get tokens
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current user info

### Incidents

- `POST /api/v1/incidents/report` - Report incident with video
- `GET /api/v1/incidents/{incident_id}` - Get incident details
- `GET /api/v1/incidents/nearby` - Get nearby incidents
- `DELETE /api/v1/incidents/{incident_id}` - Delete incident

### Users

- `GET /api/v1/users/me/incidents` - Get user's incidents
- `PATCH /api/v1/users/me` - Update user profile
- `GET /api/v1/users/me/stats` - Get user statistics

## Development Workflow

### Local Development Setup

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the development server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

4. Run Celery worker:

```bash
celery -A app.celery_app worker --loglevel=info
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest

# Run tests with coverage
pytest --cov=app tests/
```

## Database Models

### User Model
- `user_id`: UUID primary key
- `email`: Unique email address
- `username`: Unique username
- `password_hash`: Bcrypt hashed password
- `created_at`: Account creation timestamp
- `last_login`: Last login timestamp
- `is_active`: Account status

### Incident Model
- `incident_id`: UUID primary key
- `user_id`: Foreign key to user
- `type`: Incident type (crash, police, road_rage, hazard, other)
- `latitude`, `longitude`: GPS coordinates
- `timestamp`: Incident time
- `speed`, `heading`: Optional vehicle data
- `description`: Optional text description
- `video_path`: Path to stored video
- `video_size`: Video file size
- `processing_status`: Processing state (pending, processing, completed, failed)

### DetectedVehicle Model
- `detection_id`: UUID primary key
- `incident_id`: Foreign key to incident
- `vehicle_type`: Type of vehicle (car, truck, motorcycle, bus)
- `make`, `model`, `color`: Vehicle attributes
- `confidence`: Detection confidence score
- `bounding_box`: Vehicle location in frame
- `frame_timestamp`: Frame time in video

### LicensePlate Model
- `plate_id`: UUID primary key
- `incident_id`: Foreign key to incident
- `detection_id`: Optional foreign key to vehicle
- `plate_number`: Recognized plate text
- `confidence`: OCR confidence score
- `state_region`, `country`: Optional location data
- `bounding_box`: Plate location in frame
- `frame_timestamp`: Frame time in video

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `API_HOST` | API host address | `0.0.0.0` |
| `API_PORT` | API port | `8000` |
| `API_SECRET_KEY` | JWT secret key | **Required** |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token expiry | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token expiry | `7` |
| `DATABASE_URL` | MySQL connection string | **Required** |
| `REDIS_URL` | Redis connection string | `redis://redis:6379/0` |
| `VIDEO_STORAGE_PATH` | Video storage directory | `/var/data/videos` |
| `MAX_VIDEO_SIZE_MB` | Max video upload size | `500` |
| `YOLO_MODEL` | YOLO model file | `yolov8n.pt` |
| `OCR_LANGUAGES` | OCR language codes | `en` |

## Deployment Guide (Linode VPS)

### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Clone and Configure

```bash
git clone https://github.com/josephrendacec/dashcam_backend.git
cd dashcam_backend
cp .env.example .env
# Edit .env with production values
```

### 3. Deploy

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 4. Setup SSL

```bash
sudo ./scripts/setup-ssl.sh
```

### 5. Monitor Services

```bash
# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Check status
docker-compose -f docker-compose.prod.yml ps
```

## ML Model Information

### Vehicle Detection (YOLOv8)
- **Model**: YOLOv8n (nano) - lightweight and fast
- **Classes Detected**: car, truck, motorcycle, bus
- **Input**: Video frames at 1 FPS
- **Output**: Bounding boxes, confidence scores, vehicle types

### License Plate Recognition (EasyOCR)
- **Engine**: EasyOCR with English language support
- **Input**: Cropped vehicle regions or full frames
- **Output**: Plate numbers, confidence scores, bounding boxes
- **Validation**: Regex-based format validation

## Security Considerations

1. **Authentication**: JWT tokens with expiration
2. **Password Hashing**: Bcrypt with salt
3. **HTTPS**: SSL/TLS encryption in production
4. **Input Validation**: Pydantic schema validation
5. **SQL Injection**: SQLAlchemy ORM protection
6. **File Validation**: Video type and size checks
7. **CORS**: Configurable origins
8. **Rate Limiting**: (Future enhancement)

## Performance Optimization

- **Database Indexing**: Optimized queries with indexes on email, username
- **Connection Pooling**: SQLAlchemy connection pool
- **Background Processing**: Celery for async video processing
- **Video Storage**: Efficient file system storage
- **Caching**: Redis for session and task management

## Troubleshooting

### Database Connection Issues
```bash
# Check MySQL status
docker-compose ps mysql

# View MySQL logs
docker-compose logs mysql
```

### Celery Worker Issues
```bash
# Check worker status
docker-compose ps celery_worker

# View worker logs
docker-compose logs celery_worker
```

### Video Processing Failures
- Check video file format (MP4 recommended)
- Verify video storage permissions
- Review Celery worker logs for errors

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Contact

For questions or support, please open an issue on GitHub.