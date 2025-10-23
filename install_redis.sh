#!/bin/bash
# UrbanFlowAI - Redis Installation Script

echo "======================================================================"
echo " Installing Redis for UrbanFlowAI"
echo "======================================================================"
echo ""

# Update package list
echo "📦 Updating package lists..."
sudo apt update

echo ""
echo "📥 Installing Redis..."
sudo apt install -y redis-server

echo ""
echo "🔧 Starting Redis service..."
sudo systemctl start redis-server

echo ""
echo "✅ Enabling Redis to start on boot..."
sudo systemctl enable redis-server

echo ""
echo "======================================================================"
echo " Testing Redis Connection"
echo "======================================================================"
redis-cli ping

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ SUCCESS! Redis is installed and running!"
    echo ""
    echo "📊 Redis Info:"
    redis-cli --version
    echo ""
    echo "🔌 Connection: localhost:6379"
    echo ""
    echo "======================================================================"
    echo " You can now run your UrbanFlowAI scripts!"
    echo "======================================================================"
else
    echo ""
    echo "⚠️  Warning: Redis installation completed but connection test failed"
    echo "   Try manually: redis-cli ping"
fi

