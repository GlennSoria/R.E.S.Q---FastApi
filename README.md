# RESQ FastAPI

This package follows the GitHub repo structure and behavior as closely as possible:

- Models from `api/models.py`: `UserProfile`, `Camera`, `Incident`
- Endpoints from `api/urls.py`
- Serializer behavior from `api/serializers.py`
- DRF-style token header: `Authorization: Token <token>`
- Django-style table names: `auth_user`, `authtoken_token`, `api_userprofile`, `api_camera`, `api_incident`

Source repo used: `https://github.com/NBlancs/R-E-S-Q-django-rest`

## Requirements

Use Python 3.11.

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
copy .env.example .env
```

## Run

```powershell
python -m uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

## Seed Demo Data

```powershell
python scripts/seed_demo_data.py
```

Demo accounts:

```text
admin@gmail.com / admin123
bfp@gmail.com / bfp123
```

## Main Endpoints

### Authentication

```text
POST /api/auth/register/
POST /api/auth/login/
GET  /api/auth/profile/
```

### Cameras

```text
GET    /api/cameras/
POST   /api/cameras/
GET    /api/cameras/{id}/
PUT    /api/cameras/{id}/
DELETE /api/cameras/{id}/
```

### Incidents

```text
GET    /api/incidents/
POST   /api/incidents/
GET    /api/incidents/{id}/
PUT    /api/incidents/{id}/
DELETE /api/incidents/{id}/
```

### System Summary

```text
GET /api/system/overview/
```

## Auth Header

```text
Authorization: Token <your_token>
```

## PowerShell Tests

### Register

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/auth/register/" `
-Method POST `
-Body (@{
    email = "test@email.com"
    password = "123456"
    role = "bfp"
} | ConvertTo-Json) `
-ContentType "application/json"
```

### Login

```powershell
$response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/auth/login/" `
-Method POST `
-Body (@{
    email = "test@email.com"
    password = "123456"
} | ConvertTo-Json) `
-ContentType "application/json"

$token = $response.token
```

### Profile

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/auth/profile/" `
-Headers @{ Authorization = "Token $token" }
```

### Create Camera

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/cameras/" `
-Method POST `
-Headers @{ Authorization = "Token $token" } `
-Body (@{
    camera_code = "CAM-100"
    name = "Test Camera"
    location = "Office"
    status = "online"
    footage_url = ""
} | ConvertTo-Json) `
-ContentType "application/json"
```

### Create Incident

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/incidents/" `
-Method POST `
-Headers @{ Authorization = "Token $token" } `
-Body (@{
    incident_code = "INC-100"
    incident_type = "fire"
    location = "Office"
    detection_method = "manual"
    status = "investigating"
    camera = 1
    notes = "Test incident"
} | ConvertTo-Json) `
-ContentType "application/json"
```

## Notes

If you want to use an existing Django `db.sqlite3`, copy it into this folder and set `.env`:

```env
DATABASE_URL=sqlite:///./db.sqlite3
```

This package can read Django PBKDF2 password hashes created by the included code. Existing Django databases may need small schema checks if migrations differ.
