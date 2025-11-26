#!/bin/bash

echo "========================================"
echo "🔍 CHECKING RUNNING CONTAINERS"
echo "========================================"
docker ps

echo ""
echo "========================================"
echo "📜 BACKEND LOGS (Last 20 lines)"
echo "========================================"
docker logs ai-trainer-backend --tail 20

echo ""
echo "========================================"
echo "📜 FRONTEND LOGS (Last 20 lines)"
echo "========================================"
docker logs ai-trainer-frontend --tail 20

echo ""
echo "========================================"
echo "✅ Check Complete"
echo "========================================"
