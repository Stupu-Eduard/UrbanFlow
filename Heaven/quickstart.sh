#!/bin/bash
# UrbanFlowAI Quick Start Script
# This script sets up and starts the entire system

set -e

echo "🧠 UrbanFlowAI - Quick Start"
echo "=============================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

echo "✓ Docker is running"
echo ""

# Step 1: Start services
echo "📦 Starting all services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be healthy (this may take 60-90 seconds)..."
sleep 10

# Wait for API to be ready
MAX_RETRIES=30
RETRY_COUNT=0
until curl -s http://localhost:8000/health > /dev/null 2>&1; do
    RETRY_COUNT=$((RETRY_COUNT+1))
    if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
        echo "❌ API failed to start. Check logs with: docker-compose logs api"
        exit 1
    fi
    echo "Waiting for API... (attempt $RETRY_COUNT/$MAX_RETRIES)"
    sleep 3
done

echo "✓ All services are running"
echo ""

# Step 2: Initialize database
echo "🗄️  Initializing database with sample data..."
curl -s -X POST http://localhost:8000/api/v1/admin/seed-data > /dev/null
echo "✓ Database seeded"

# Step 3: Initialize Redis
echo "💾 Initializing Redis with sample real-time data..."
curl -s -X POST http://localhost:8000/api/v1/admin/seed-redis > /dev/null
echo "✓ Redis seeded"
echo ""

# Step 4: Test the API
echo "🧪 Testing API..."
HEALTH_STATUS=$(curl -s http://localhost:8000/health | grep -o '"status":"[^"]*"' | cut -d'"' -f4)

if [ "$HEALTH_STATUS" == "healthy" ]; then
    echo "✓ API is healthy"
else
    echo "⚠️  API status: $HEALTH_STATUS"
fi
echo ""

# Success message
echo "=============================="
echo "✨ UrbanFlowAI is ready!"
echo "=============================="
echo ""
echo "🌐 Access points:"
echo "   API:          http://localhost:8000"
echo "   Documentation: http://localhost:8000/docs"
echo "   Health:       http://localhost:8000/health"
echo ""
echo "📊 Test commands:"
echo "   Live Status:  curl http://localhost:8000/api/v1/status/live"
echo "   View Logs:    docker-compose logs -f api"
echo "   Stop System:  docker-compose down"
echo ""
echo "📚 Next steps:"
echo "   1. Open http://localhost:8000/docs in your browser"
echo "   2. Try the '/api/v1/status/live' endpoint"
echo "   3. Try the '/api/v1/route/calculate' endpoint"
echo ""
echo "Happy coding! 🚀"

