#!/bin/bash

# Database Backup Restore Script
# This script restores the PostgreSQL database from backup.sql

set -e

echo "🔄 Starting database restore process..."

# Check if backup file exists
if [ ! -f "db/backup.sql" ]; then
    echo "❌ Error: db/backup.sql not found!"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running!"
    exit 1
fi

# Start PostgreSQL if not running
echo "📦 Starting PostgreSQL container..."
docker compose up -d postgres

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 5

# Check if database is healthy
if ! docker compose exec -T postgres pg_isready -U todo_user -d todo_db > /dev/null 2>&1; then
    echo "❌ Error: PostgreSQL is not ready!"
    exit 1
fi

# Restore the database
echo "📥 Restoring database from backup..."
docker compose exec -T postgres psql -U todo_user -d todo_db < db/backup.sql

echo "✅ Database restored successfully!"
echo ""
echo "🚀 You can now start the application with:"
echo "   docker compose up -d"
echo ""
echo "📊 Access the application at:"
echo "   - Web Interface: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
