#!/bin/bash
# Test script for production endpoints

echo "🧪 Testing Clinical Assistant Production Endpoints"
echo "=================================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Test 1: Frontend
echo "1️⃣  Testing Frontend..."
STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/)
if [ "$STATUS" -eq 200 ]; then
    echo -e "${GREEN}✅ Frontend: OK${NC}"
else
    echo -e "${RED}❌ Frontend: FAILED (${STATUS})${NC}"
fi

# Test 2: Health Check
echo "2️⃣  Testing Health Check..."
HEALTH=$(curl -s http://localhost:8000/api/v1/health)
if [[ $HEALTH == *"healthy"* ]]; then
    echo -e "${GREEN}✅ Health Check: OK${NC}"
    echo "   Response: $HEALTH"
else
    echo -e "${RED}❌ Health Check: FAILED${NC}"
fi

# Test 3: Detailed Health
echo "3️⃣  Testing Detailed Health..."
STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/health/detailed)
if [ "$STATUS" -eq 200 ]; then
    echo -e "${GREEN}✅ Detailed Health: OK${NC}"
else
    echo -e "${RED}❌ Detailed Health: FAILED (${STATUS})${NC}"
fi

# Test 4: Readiness Probe
echo "4️⃣  Testing Readiness Probe..."
STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/health/ready)
if [ "$STATUS" -eq 200 ]; then
    echo -e "${GREEN}✅ Readiness Probe: OK${NC}"
else
    echo -e "${RED}❌ Readiness Probe: FAILED (${STATUS})${NC}"
fi

# Test 5: Liveness Probe
echo "5️⃣  Testing Liveness Probe..."
STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/health/live)
if [ "$STATUS" -eq 200 ]; then
    echo -e "${GREEN}✅ Liveness Probe: OK${NC}"
else
    echo -e "${RED}❌ Liveness Probe: FAILED (${STATUS})${NC}"
fi

# Test 6: Prometheus Metrics
echo "6️⃣  Testing Prometheus Metrics..."
METRICS=$(curl -s http://localhost:8000/metrics | grep -c "http_requests_total")
if [ "$METRICS" -gt 0 ]; then
    echo -e "${GREEN}✅ Prometheus Metrics: OK${NC}"
    echo "   Found $METRICS metric lines"
else
    echo -e "${RED}❌ Prometheus Metrics: FAILED${NC}"
fi

# Test 7: API Documentation
echo "7️⃣  Testing API Docs..."
STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs)
if [ "$STATUS" -eq 200 ]; then
    echo -e "${GREEN}✅ API Docs: OK${NC}"
else
    echo -e "${RED}❌ API Docs: FAILED (${STATUS})${NC}"
fi

echo ""
echo "=================================================="
echo "🎉 All production endpoints tested!"
echo ""
echo "📊 Available URLs:"
echo "   - Frontend:        http://localhost:8000"
echo "   - API Docs:        http://localhost:8000/docs"
echo "   - Health:          http://localhost:8000/api/v1/health"
echo "   - Detailed Health: http://localhost:8000/api/v1/health/detailed"
echo "   - Metrics:         http://localhost:8000/metrics"
