#!/bin/bash
set -e

PROJECT_DIR="/home/admin/Posture-Thesis-System"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"
VENV_DIR="$BACKEND_DIR/venv"

echo "=== Posture Thesis System Deployment ==="

# 1. Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# 2. Install backend dependencies
echo "Installing backend dependencies..."
"$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install -r "$BACKEND_DIR/requirements.txt"

# 3. Copy .env if not exists
if [ ! -f "$BACKEND_DIR/.env" ]; then
    echo "Copying .env.example to .env..."
    cp "$PROJECT_DIR/.env.example" "$BACKEND_DIR/.env"
fi

# 4. Seed database
echo "Seeding database..."
cd "$BACKEND_DIR"
"$VENV_DIR/bin/python" -m app.seed.seed_data

# 5. Build frontend
echo "Building frontend..."
cd "$FRONTEND_DIR"
npm install
npm run build

# 6. Install systemd service
echo "Installing systemd service..."
sudo cp "$PROJECT_DIR/deploy/posture-backend.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable posture-backend
sudo systemctl restart posture-backend

echo ""
echo "=== Deployment Complete ==="
echo "Backend + Frontend: http://$(hostname -I | awk '{print $1}')/api/health"
echo ""
echo "Default credentials:"
echo "  User:  user / pass123"
echo "  Admin: admin / admin123"
