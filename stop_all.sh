#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${RED}Stopping Distributed Cafeteria System...${NC}"

# 1. Stop Backend and Frontend
echo "----------------------------------------"
echo "Step 1: Stopping Application Services..."

# Stop Backend (uvicorn)
if pkill -f "uvicorn main:app"; then
    echo -e "${GREEN}Backend stopped.${NC}"
else
    echo "Backend not running or already stopped."
fi

# Stop Frontend (vite)
if pkill -f "vite"; then
    echo -e "${GREEN}Frontend stopped.${NC}"
else
    echo "Frontend not running or already stopped."
fi

# 2. Stop Databases
echo "----------------------------------------"
echo "Step 2: Stopping Databases..."


echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   System Stopped Successfully!   ${NC}"
echo -e "${GREEN}========================================${NC}"
