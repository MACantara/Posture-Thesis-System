# Railway Deployment Guide

This guide explains how to deploy the Posture Thesis System to Railway as two separate services.

## Overview

The application is deployed as two Railway services:

- **Backend service** (`backend/` root): FastAPI app served via uvicorn, auto-detected by Railpack's Python provider
- **Frontend service** (`frontend/` root): React app built with Vite, served as a static site by Railpack's Node provider (Caddy)
- **PostgreSQL database**: Railway-managed PostgreSQL instance

## Prerequisites

- Railway account (https://railway.app)
- GitHub repository with the project code
- Railway CLI (optional, for local management)

## Step 1: Create Railway Project

1. Log in to Railway
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your Posture-Thesis-System repository

## Step 2: Add PostgreSQL Database

1. In your Railway project, click "New Service"
2. Select "Database" → "PostgreSQL"
3. Railway will create a PostgreSQL instance and provide a `DATABASE_URL` environment variable

## Step 3: Create the Backend Service

1. Click "New Service" → "GitHub Repo" → select your repository
2. In the service settings, set **Root Directory** to `backend`
3. Railway will detect `backend/railway.toml` and use Railpack to build
4. Railpack auto-detects Python via `requirements.txt`, creates a venv, and installs dependencies

### Backend Environment Variables

Navigate to the backend service → Variables tab and add:

| Variable | Value | Description |
|----------|-------|-------------|
| `DB_BACKEND` | `postgresql` | Use PostgreSQL instead of SQLite |
| `DATABASE_URL` | *(reference PostgreSQL service)* | Click "Add Variable Reference" and select the PostgreSQL service's `DATABASE_URL` |
| `SECRET_KEY` | *(generate one)* | JWT signing key — generate with `python -m app.config generate-secret` |
| `CORS_ORIGINS` | *(frontend URL)* | Set to your frontend service's Railway domain (e.g., `https://frontend-service.railway.app`) |

### Optional Backend Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `USE_MOCK_SENSORS` | `True` | Set to `False` if deploying with actual hardware sensors |
| `HOST` | `0.0.0.0` | Server host (keep default for Railway) |
| `PORT` | `8000` | Server port (Railway sets `$PORT` automatically) |
| `WORKERS` | `1` | Number of uvicorn workers |

### Sensor Configuration (if using real hardware)

| Variable | Default | Description |
|----------|---------|-------------|
| `I2C_BUS` | `1` | I2C bus number |
| `MPU6050_ADDRESS` | `0x68` | MPU6050 sensor I2C address |
| `SERVO_GPIO_PIN` | `18` | GPIO pin for servo motor |
| `VIBRATOR_GPIO_PIN` | `23` | GPIO pin for vibration motor |
| `SENSOR_SAMPLE_RATE` | `10` | Sensor sample rate in Hz |

### Posture Detection Thresholds

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTURE_ANGLE_THRESHOLD_GOOD` | `10` | Angle threshold (degrees) for "good" posture |
| `POSTURE_ANGLE_THRESHOLD_WARNING` | `20` | Angle threshold (degrees) for "warning" posture |

## Step 4: Create the Frontend Service

1. Click "New Service" → "GitHub Repo" → select your repository
2. In the service settings, set **Root Directory** to `frontend`
3. Railpack auto-detects Vite via `vite.config.ts`, builds with `npm run build`, and serves the `dist/` directory as a static site with SPA fallback via Caddy

### Frontend Environment Variables

These variables are embedded at build time (VITE_ prefix required):

| Variable | Value | Description |
|----------|-------|-------------|
| `VITE_API_URL` | *(backend URL)* | Backend service URL (e.g., `https://backend-service.railway.app`) |
| `VITE_WS_URL` | *(backend WS URL)* | Backend WebSocket URL (e.g., `wss://backend-service.railway.app`) |

Set these in the frontend service → Variables tab. Reference the backend service's public URL.

## Step 5: Generate SECRET_KEY

Run this command locally to generate a secure secret key:

```bash
cd backend
python -m app.config generate-secret
```

Copy the generated key and set it as the `SECRET_KEY` environment variable in the backend Railway service.

## Step 6: Deploy

1. Push your changes to GitHub
2. Railway will automatically detect the changes and redeploy both services
3. The backend build (Railpack) will:
   - Install Python dependencies from `requirements.txt` into a virtualenv
   - Start the FastAPI server via uvicorn
4. The frontend build (Railpack) will:
   - Install Node dependencies with `npm install`
   - Build the React app with `npm run build`
   - Serve the `dist/` directory as a static site with SPA fallback

## Step 7: Seed Database (Optional)

After deployment, you may want to seed the database with demo users. You can do this by:

1. Accessing the Railway service logs
2. Running a one-time command via Railway CLI or by temporarily adding a startup script

Alternatively, create users through the API endpoints after deployment.

## Step 8: Access Your Application

Once deployment is complete:

1. Railway will provide public URLs for both services
2. Access the frontend at the frontend service URL (e.g., `https://frontend-service.railway.app`)
3. The API health check is available at the backend service URL (e.g., `https://backend-service.railway.app/api/health`)

## Default Credentials

If you seeded the database, use these credentials:

| Role | Username | Password |
|---|---|---|
| User | `user` | `pass123` |
| Admin | `admin` | `admin123` |

## Troubleshooting

### Build Fails

- Check the Railway build logs for errors
- Ensure the **Root Directory** is set correctly for each service (`backend/` and `frontend/`)
- Backend: ensure `backend/railway.toml` exists with the correct start command
- Frontend: Railpack auto-detects Vite — no config file needed
- Override Python/Node versions with `RAILPACK_PYTHON_VERSION` / `RAILPACK_NODE_VERSION` env vars if needed

### Database Connection Errors

- Ensure the PostgreSQL service is linked to the backend service
- Verify `DB_BACKEND=postgresql` is set on the backend service
- Check that `DATABASE_URL` references the PostgreSQL service

### Frontend Can't Reach Backend

- Verify `VITE_API_URL` is set to the backend's public URL (with `https://`)
- Verify `VITE_WS_URL` is set to the backend's WebSocket URL (with `wss://`)
- These are build-time variables — redeploy the frontend after changing them

### CORS Errors

- Set `CORS_ORIGINS` on the backend service to the frontend's Railway domain
- Include any custom domains if you've configured them

## Local Development vs Production

- **Local**: Uses SQLite (`DB_BACKEND=sqlite` by default), runs with hot reload, frontend dev server on port 5173
- **Railway**: Uses PostgreSQL (`DB_BACKEND=postgresql`), no reload, frontend served as static files

The application automatically detects the environment based on the `DB_BACKEND` setting.

## Monitoring

- Railway provides built-in logs for each service
- Monitor database usage in the PostgreSQL service dashboard
- Set up alerts for CPU/memory usage if needed

## Custom Domains (Optional)

1. In Railway, go to your service → Settings → Domains
2. Add your custom domain
3. Update DNS records as instructed by Railway
4. Update `CORS_ORIGINS` on the backend to include the frontend's custom domain
5. Update `VITE_API_URL` and `VITE_WS_URL` on the frontend to use the backend's custom domain
