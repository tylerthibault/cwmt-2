#!/bin/bash
# Reset Database Script for Linux/Mac
# This script deletes the database and seed flag to force a fresh seed on next startup

echo "🗑️  Resetting database..."

# Delete database file
if [ -f "instance/cwmt.db" ]; then
    rm instance/cwmt.db
    echo "✓ Deleted instance/cwmt.db"
else
    echo "ℹ️  instance/cwmt.db not found"
fi

# Delete seed flag
if [ -f "instance/.seeded" ]; then
    rm instance/.seeded
    echo "✓ Deleted instance/.seeded"
else
    echo "ℹ️  instance/.seeded not found"
fi

echo ""
echo "✅ Database reset complete!"
echo "🚀 Run 'python run.py' to start the app with fresh seeded data"
