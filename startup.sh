#!/bin/bash

# Default ports
FRONTEND_PORT=3001
BACKEND_PORT=8001
DB_PORT=5432

# Detect VM IP if available
VM_IP=$(hostname -I | awk '{print $1}')
IS_VM=false

if [[ "$VM_IP" != "127.0.0.1" && "$VM_IP" != "" ]]; then
    IS_VM=true
fi

if $IS_VM; then
    echo "Detected VM environment"
    FRONTEND_URL="http://${VM_IP}:${FRONTEND_PORT}"
    BACKEND_URL="http://${VM_IP}:${BACKEND_PORT}"
    API_URL="http://${VM_IP}:${BACKEND_PORT}"
    CORS_ORIGINS="http://localhost:${FRONTEND_PORT},http://localhost:3000,http://${VM_IP}:${FRONTEND_PORT}"
else
    echo "Detected local environment"
    FRONTEND_URL="http://localhost:${FRONTEND_PORT}"
    BACKEND_URL="http://localhost:${BACKEND_PORT}"
    API_URL="http://localhost:${BACKEND_PORT}"
    CORS_ORIGINS="http://localhost:${FRONTEND_PORT},http://localhost:3000"
fi

# ✅ Export for local shell usage
export NEXT_PUBLIC_API_URL=${API_URL}
export FRONTEND_PORT=${FRONTEND_PORT}
export BACKEND_PORT=${BACKEND_PORT}
export DB_PORT=${DB_PORT}

# ✅ Write to frontend/.env.production for Next.js
cat > frontend/.env.production << EOL
NEXT_PUBLIC_API_URL=${API_URL}
EOL

# ✅ Write to .env for Docker Compose
cat > .env << EOL
NEXT_PUBLIC_API_URL=${API_URL}
FRONTEND_PORT=${FRONTEND_PORT}
BACKEND_PORT=${BACKEND_PORT}
DB_PORT=${DB_PORT}
CORS_ORIGINS=${CORS_ORIGINS}
EOL

echo "Starting database..."
docker compose --profile prod up -d db-prod

echo "Waiting for database to be ready..."
sleep 10

echo "Starting backend..."
docker compose --profile prod up -d backend-prod

echo "Waiting for backend to be ready..."
sleep 10

echo "Inserting data into database..."
docker compose --profile prod exec backend-prod python -m app.database.insert_data

echo "Rebuilding frontend with correct API URL..."
# Force remove the frontend container and its image to ensure clean rebuild
docker compose --profile prod rm -f frontend-prod
docker compose --profile prod build --no-cache frontend-prod
docker compose --profile prod up -d frontend-prod

echo "Setup complete! Your application is now running at:"
echo "Frontend: ${FRONTEND_URL}"
echo "Backend: ${BACKEND_URL}"
