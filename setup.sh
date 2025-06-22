#!/bin/bash

# CacheOut Containerized Testing Environment Setup Script

set -e

echo "🚀 Setting up CacheOut Containerized Testing Environment"
echo "=================================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp backend/env.example .env
    echo "✅ .env file created. Please edit it with your configuration."
else
    echo "✅ .env file already exists."
fi

# Build and start containers
echo "🔨 Building and starting containers..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
echo "🔍 Checking service status..."
docker-compose ps

# Test backend health
echo "🏥 Testing backend health..."
if curl -f http://localhost:8000/api/v1/health > /dev/null 2>&1; then
    echo "✅ Backend is healthy!"
else
    echo "⚠️  Backend health check failed. Check logs with: docker-compose logs coordinator"
fi

# Test frontend
echo "🌐 Testing frontend..."
if curl -f http://localhost:5173 > /dev/null 2>&1; then
    echo "✅ Frontend is accessible!"
else
    echo "⚠️  Frontend check failed. Check logs with: docker-compose logs frontend"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Access URLs:"
echo "   Frontend: http://localhost:5173"
echo "   Backend API: http://localhost:8000"
echo "   Health Check: http://localhost:8000/api/v1/health"
echo ""
echo "🔧 Useful commands:"
echo "   View logs: docker-compose logs"
echo "   Stop services: docker-compose down"
echo "   Restart services: docker-compose restart"
echo "   Scale workers: docker-compose up -d --scale worker=3"
echo ""
echo "🧪 Run tests:"
echo "   cd testing && python test_integration.py"
echo ""
echo "📖 For more information, see README.md" 