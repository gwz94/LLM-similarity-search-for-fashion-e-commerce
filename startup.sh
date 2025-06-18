#!/bin/bash

# Default ports
FRONTEND_PORT=3001
BACKEND_PORT=8001
DB_PORT=5432

# Accept profile (default: prod)
PROFILE=${1:-prod}
BACKEND_ENV_FILE="backend/.env.${PROFILE}"
FRONTEND_ENV_FILE="frontend/.env.${PROFILE}"
COMPOSE_PROFILE="${PROFILE}"

echo "Environment: $PROFILE"

# Detect VM IP if available
# To handle deployment on VM
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

# Export for Docker Compose
export NEXT_PUBLIC_API_URL=${API_URL}
export FRONTEND_PORT=${FRONTEND_PORT}
export BACKEND_PORT=${BACKEND_PORT}
export DB_PORT=${DB_PORT}

# Write to frontend/.env.[profile] for Next.js
cat > "${FRONTEND_ENV_FILE}" << EOL
NEXT_PUBLIC_API_URL=${API_URL}
EOL

# Write to .env for Docker Compose (Compose only reads .env in root)
cat > .env << EOL
NEXT_PUBLIC_API_URL=${API_URL}
FRONTEND_PORT=${FRONTEND_PORT}
BACKEND_PORT=${BACKEND_PORT}
DB_PORT=${DB_PORT}
CORS_ORIGINS=${CORS_ORIGINS}
EOL

# Safely update or append CORS_ORIGINS to backend/.env.[profile]
if grep -q "^CORS_ORIGINS=" "$BACKEND_ENV_FILE"; then
    sed -i "s|^CORS_ORIGINS=.*|CORS_ORIGINS=${CORS_ORIGINS}|" "$BACKEND_ENV_FILE"
else
    echo "CORS_ORIGINS=${CORS_ORIGINS}" >> "$BACKEND_ENV_FILE"
fi

echo "Starting database..."
docker compose --profile "$COMPOSE_PROFILE" up -d db-${PROFILE}

echo "Waiting for database to be ready..."
sleep 10

echo "Starting backend..."
docker compose --profile "$COMPOSE_PROFILE" up -d backend-${PROFILE}

echo "Waiting for backend to be ready..."
sleep 10

echo "Inserting data into database..."
docker compose --profile "$COMPOSE_PROFILE" exec backend-${PROFILE} python -m app.database.insert_data

echo "Rebuilding frontend with correct API URL..."
docker compose --profile "$COMPOSE_PROFILE" rm -f frontend-${PROFILE}
docker compose --profile "$COMPOSE_PROFILE" build --no-cache frontend-${PROFILE}
docker compose --profile "$COMPOSE_PROFILE" up -d frontend-${PROFILE}

echo "Setup complete!"
echo "Frontend: ${FRONTEND_URL}"
echo "Backend: ${BACKEND_URL}"
