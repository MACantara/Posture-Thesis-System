# Deployment Guide

## Raspberry Pi 3 B+ Deployment

### Prerequisites

- Raspberry Pi 3 B+ with Raspberry Pi OS
- Python 3.9+ installed
- Node.js 18+ installed
- Network connection (WiFi or Ethernet)

### Quick Deploy

1. Clone the repository to the Pi:
```bash
cd /home/pi
git clone <repo-url> Posture-Thesis-System
cd Posture-Thesis-System
```

2. Run the deployment script:
```bash
chmod +x deploy/deploy.sh
./deploy/deploy.sh
```

The script will:
- Create a Python virtual environment
- Install backend dependencies
- Copy `.env.example` to `.env`
- Seed the database with demo data
- Build the frontend
- Install and start the systemd service
- Configure nginx as reverse proxy

### Manual Setup

#### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env
python -m app.seed.seed_data
python run.py
```

#### Frontend
```bash
cd frontend
npm install
npm run build
```

### systemd Service

The backend runs as a systemd service:

```bash
sudo systemctl status posture-backend
sudo systemctl restart posture-backend
sudo systemctl stop posture-backend
```

Service file: `deploy/posture-backend.service`

### nginx Configuration

nginx serves the frontend and proxies API/WebSocket:

```bash
sudo nginx -t
sudo systemctl restart nginx
```

Config file: `deploy/nginx-posture.conf`

### Access

After deployment, the system is accessible at:
- **Frontend**: `http://<pi-ip>/`
- **API Health**: `http://<pi-ip>/api/health`
- **WebSocket**: `ws://<pi-ip>/ws?token=<jwt>`

Find the Pi's IP with:
```bash
hostname -I
```

### Default Credentials

- **User**: `user` / `pass123`
- **Admin**: `admin` / `admin123`

Change these after first login in production.

### Troubleshooting

- **Backend not starting**: Check `sudo journalctl -u posture-backend -f`
- **nginx errors**: Check `sudo nginx -t` and `/var/log/nginx/error.log`
- **I2C not working**: Ensure I2C is enabled via `raspi-config`
- **Port conflicts**: Ensure nothing else is using port 8000 or 80
