# API Usage Examples

This document provides practical examples of how to use the Dashcam Backend API.

## Base URL

- Development: `http://localhost:8000`
- Production: `https://your-domain.com`

All API endpoints are prefixed with `/api/v1`.

## Authentication Flow

### 1. Register a New User

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "dashcam_user",
    "password": "SecurePassword123!"
  }'
```

Response:
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "username": "dashcam_user",
  "created_at": "2024-01-13T12:00:00"
}
```

### 2. Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### 3. Refresh Token

```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

### 4. Get Current User Info

```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Incident Management

### 1. Report an Incident with Video

```bash
curl -X POST http://localhost:8000/api/v1/incidents/report \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "video=@/path/to/dashcam_video.mp4" \
  -F "type=crash" \
  -F "latitude=37.7749" \
  -F "longitude=-122.4194" \
  -F "timestamp=2024-01-13T10:30:00Z" \
  -F "speed=65.5" \
  -F "heading=90.0" \
  -F "description=Rear-end collision on Highway 101"
```

Response:
```json
{
  "incident_id": "987e6543-e21b-12d3-a456-426614174999",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "type": "crash",
  "latitude": 37.7749,
  "longitude": -122.4194,
  "timestamp": "2024-01-13T10:30:00",
  "speed": 65.5,
  "heading": 90.0,
  "description": "Rear-end collision on Highway 101",
  "video_path": "/var/data/videos/123e4567.../987e6543.../raw.mp4",
  "video_size": 52428800,
  "processing_status": "pending",
  "created_at": "2024-01-13T12:00:00",
  "detected_vehicles": []
}
```

### 2. Get Incident Details

```bash
curl -X GET http://localhost:8000/api/v1/incidents/987e6543-e21b-12d3-a456-426614174999 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Response includes detected vehicles and license plates after processing:
```json
{
  "incident_id": "987e6543-e21b-12d3-a456-426614174999",
  "type": "crash",
  "processing_status": "completed",
  "detected_vehicles": [
    {
      "detection_id": "det-001",
      "vehicle_type": "car",
      "color": "red",
      "confidence": 0.95,
      "bounding_box": {"x1": 100, "y1": 200, "x2": 300, "y2": 400},
      "frame_timestamp": 5.0
    }
  ]
}
```

### 3. Get Nearby Incidents

```bash
curl -X GET "http://localhost:8000/api/v1/incidents/nearby?latitude=37.7749&longitude=-122.4194&radius_km=5&time_window_hours=24" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Response:
```json
[
  {
    "incident_id": "987e6543-e21b-12d3-a456-426614174999",
    "type": "crash",
    "latitude": 37.7749,
    "longitude": -122.4194,
    "timestamp": "2024-01-13T10:30:00",
    "distance_km": 0.5,
    "processing_status": "completed"
  },
  {
    "incident_id": "456e7890-e21b-12d3-a456-426614174888",
    "type": "police",
    "latitude": 37.7800,
    "longitude": -122.4150,
    "timestamp": "2024-01-13T09:15:00",
    "distance_km": 2.3,
    "processing_status": "completed"
  }
]
```

### 4. Delete an Incident

```bash
curl -X DELETE http://localhost:8000/api/v1/incidents/987e6543-e21b-12d3-a456-426614174999 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Response:
```json
{
  "message": "Incident deleted successfully"
}
```

## User Management

### 1. Get User's Incidents

```bash
curl -X GET "http://localhost:8000/api/v1/users/me/incidents?page=1&per_page=10&type_filter=crash" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 2. Update User Profile

```bash
curl -X PATCH http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "new_username",
    "email": "newemail@example.com"
  }'
```

### 3. Get User Statistics

```bash
curl -X GET http://localhost:8000/api/v1/users/me/stats \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Response:
```json
{
  "total_incidents": 15,
  "reports_by_type": {
    "crash": 5,
    "police": 3,
    "road_rage": 2,
    "hazard": 4,
    "other": 1
  }
}
```

## Python Client Example

```python
import requests
from pathlib import Path

class DashcamClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.access_token = None
        self.refresh_token = None
    
    def register(self, email, username, password):
        """Register a new user."""
        response = requests.post(
            f"{self.base_url}/api/v1/auth/register",
            json={
                "email": email,
                "username": username,
                "password": password
            }
        )
        response.raise_for_status()
        return response.json()
    
    def login(self, email, password):
        """Login and store tokens."""
        response = requests.post(
            f"{self.base_url}/api/v1/auth/login",
            json={"email": email, "password": password}
        )
        response.raise_for_status()
        data = response.json()
        self.access_token = data["access_token"]
        self.refresh_token = data["refresh_token"]
        return data
    
    def report_incident(self, video_path, incident_type, latitude, longitude, 
                       timestamp, speed=None, heading=None, description=None):
        """Report an incident with video upload."""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        with open(video_path, 'rb') as video_file:
            files = {'video': video_file}
            data = {
                'type': incident_type,
                'latitude': str(latitude),
                'longitude': str(longitude),
                'timestamp': timestamp,
            }
            if speed:
                data['speed'] = str(speed)
            if heading:
                data['heading'] = str(heading)
            if description:
                data['description'] = description
            
            response = requests.post(
                f"{self.base_url}/api/v1/incidents/report",
                headers=headers,
                files=files,
                data=data
            )
            response.raise_for_status()
            return response.json()
    
    def get_incident(self, incident_id):
        """Get incident details."""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(
            f"{self.base_url}/api/v1/incidents/{incident_id}",
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_nearby_incidents(self, latitude, longitude, radius_km=5, 
                           time_window_hours=24, types=None):
        """Get nearby incidents."""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "radius_km": radius_km,
            "time_window_hours": time_window_hours
        }
        if types:
            params["types"] = ",".join(types)
        
        response = requests.get(
            f"{self.base_url}/api/v1/incidents/nearby",
            headers=headers,
            params=params
        )
        response.raise_for_status()
        return response.json()

# Usage example
if __name__ == "__main__":
    client = DashcamClient()
    
    # Register and login
    client.register("user@example.com", "testuser", "SecurePass123!")
    client.login("user@example.com", "SecurePass123!")
    
    # Report incident
    incident = client.report_incident(
        video_path="dashcam_video.mp4",
        incident_type="crash",
        latitude=37.7749,
        longitude=-122.4194,
        timestamp="2024-01-13T10:30:00Z",
        speed=65.5,
        description="Rear-end collision"
    )
    print(f"Reported incident: {incident['incident_id']}")
    
    # Get nearby incidents
    nearby = client.get_nearby_incidents(37.7749, -122.4194, radius_km=10)
    print(f"Found {len(nearby)} nearby incidents")
```

## JavaScript/Fetch Example

```javascript
class DashcamAPI {
  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
    this.accessToken = null;
  }

  async register(email, username, password) {
    const response = await fetch(`${this.baseUrl}/api/v1/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, username, password })
    });
    return response.json();
  }

  async login(email, password) {
    const response = await fetch(`${this.baseUrl}/api/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    const data = await response.json();
    this.accessToken = data.access_token;
    return data;
  }

  async reportIncident(videoFile, incidentData) {
    const formData = new FormData();
    formData.append('video', videoFile);
    Object.keys(incidentData).forEach(key => {
      formData.append(key, incidentData[key]);
    });

    const response = await fetch(`${this.baseUrl}/api/v1/incidents/report`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${this.accessToken}` },
      body: formData
    });
    return response.json();
  }

  async getNearbyIncidents(latitude, longitude, radiusKm = 5) {
    const params = new URLSearchParams({
      latitude,
      longitude,
      radius_km: radiusKm
    });
    
    const response = await fetch(
      `${this.baseUrl}/api/v1/incidents/nearby?${params}`,
      {
        headers: { 'Authorization': `Bearer ${this.accessToken}` }
      }
    );
    return response.json();
  }
}

// Usage
const api = new DashcamAPI();
await api.login('user@example.com', 'SecurePass123!');
const incidents = await api.getNearbyIncidents(37.7749, -122.4194, 10);
console.log('Nearby incidents:', incidents);
```

## Error Handling

The API uses standard HTTP status codes:

- `200 OK` - Request succeeded
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required or invalid token
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `413 Payload Too Large` - File size exceeds limit
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

Error response format:
```json
{
  "detail": "Error message describing what went wrong"
}
```

## Rate Limiting

Currently, rate limiting is not implemented but will be added in future versions. Recommended client-side rate limiting:
- Auth endpoints: 5 requests per minute
- Upload endpoints: 1 request per 10 seconds
- Query endpoints: 30 requests per minute
