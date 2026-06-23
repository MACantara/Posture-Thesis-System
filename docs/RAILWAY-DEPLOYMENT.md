# Railway Deployment Guide

This guide explains how to deploy the Posture Thesis System to Railway.

## Overview

The application is deployed as a single Railway service that:
- Runs the FastAPI backend
- Serves the React frontend as static files
- Uses Railway's PostgreSQL database

## Prerequisites

- Railway account (https://railway.app)
- GitHub repository with the project code
- Railway CLI (optional, for local management)

## Step 1: Create Railway Project

1. Log in to Railway
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your Posture-Thesis-System repository
4. Railway will detect the `railway.toml` and `railpack.json` automatically

## Step 2: Add PostgreSQL Database

1. In your Railway project, click "New Service"
2. Select "Database" → "PostgreSQL"
3. Railway will create a PostgreSQL instance and provide a `DATABASE_URL` environment variable

## Step 3: Configure Environment Variables

Navigate to your web service in Railway and add the following environment variables:

### Required Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `DB_BACKEND` | `postgresql` | Use PostgreSQL instead of SQLite |
| `DATABASE_URL` | *(auto-filled)* | Railway provides this automatically when you link the PostgreSQL service |
| `SECRET_KEY` | *(generate one)* | JWT signing key - generate with `python -m app.config generate-secret` |
| `FRONTEND_DIST_PATH` | `frontend/dist` | Path to built frontend files (set automatically by `railpack.json`) |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CORS_ORIGINS` | `http://localhost:5173,http://localhost:80` | Comma-separated list of allowed origins. Set to your Railway domain (e.g., `https://your-app.railway.app`) |
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

## Step 4: Generate SECRET_KEY

Run this command locally to generate a secure secret key:

```bash
cd backend
python -m app.config generate-secret
```

Copy the generated key and set it as the `SECRET_KEY` environment variable in Railway.

## Step 5: Deploy

1. Push your changes to GitHub
2. Railway will automatically detect the changes and redeploy
3. The build process (powered by Railpack) will:
   - Install Python dependencies from `backend/requirements.txt`
   - Install frontend dependencies and build the React app (`npm run build`)
   - Start the FastAPI server via uvicorn

## Step 6: Seed Database (Optional)

After deployment, you may want to seed the database with demo users. You can do this by:

1. Accessing the Railway service logs
2. Running a one-time command via Railway CLI or by temporarily adding a startup script

Alternatively, create users through the API endpoints after deployment.

## Step 7: Access Your Application

Once deployment is complete:

1. Railway will provide a public URL (e.g., `https://your-app.railway.app`)
2. Access the application at this URL
3. The API health check is available at `https://your-app.railway.app/api/health`

## Default Credentials

If you seeded the database, use these credentials:

| Role | Username | Password |
|---|---|---|
| User | `user` | `pass123` |
| Admin | `admin` | `admin123` |

## Troubleshooting

### Build Fails

- Check the Railway build logs for errors
- Ensure `railway.toml` and `railpack.json` are in the repository root
- Railpack auto-detects Python and Node.js versions; override with `RAILPACK_PYTHON_VERSION` env var if needed

### Database Connection Errors

- Ensure the PostgreSQL service is linked to your web service
- Verify `DB_BACKEND=postgresql` is set
- Check that `DATABASE_URL` is auto-filled by Railway

### Frontend Not Loading

- Check that the frontend build completed successfully in build logs
- Verify `FRONTEND_DIST_PATH` points to the correct location
- Ensure static file mounting is working (check backend logs)

### CORS Errors

- Set `CORS_ORIGINS` to your Railway domain: `https://your-app.railway.app`
- Include any custom domains if you've configured them

## Local Development vs Production

- **Local**: Uses SQLite (`DB_BACKEND=sqlite` by default), runs with hot reload
- **Railway**: Uses PostgreSQL (`DB_BACKEND=postgresql`), no reload, serves static frontend

The application automatically detects the environment based on the `DB_BACKEND` setting.

## Monitoring

- Railway provides built-in logs for your service
- Monitor database usage in the PostgreSQL service dashboard
- Set up alerts for CPU/memory usage if needed

## Custom Domains (Optional)

1. In Railway, go to your web service → Settings → Domains
2. Add your custom domain
3. Update DNS records as instructed by Railway
4. Update `CORS_ORIGINS` to include your custom domain
