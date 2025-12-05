#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Distributed Cafeteria System...${NC}"

# Get the absolute path of the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# 1. Start Docker Containers
echo "----------------------------------------"
echo "Step 1: Starting Databases (MongoDB & Redis)..."
sudo systemctl start redis-server
sudo systemctl start mongod

# 2. Start Backend
echo "----------------------------------------"
echo "Step 2: Starting Backend..."
cd backend || exit

# Check for virtual environment
if [ -d "../venv" ]; then
    source ../venv/bin/activate
else
    echo -e "${RED}Warning: Virtual environment not found at ../venv${NC}"
fi

# Check if uvicorn is available
if ! command -v uvicorn &> /dev/null; then
    echo -e "${RED}Error: uvicorn not found. Please install dependencies.${NC}"
    exit 1
fi

# Kill existing uvicorn process if any (optional, but good for restart)
# pkill -f "uvicorn main:app" 

nohup uvicorn main:app --reload --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}Backend running (PID: $BACKEND_PID)${NC}"

# 3. Start Frontend
echo "----------------------------------------"
echo "Step 3: Starting Frontend..."
cd ../frontend || exit
nohup npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo -e "${GREEN}Frontend running (PID: $FRONTEND_PID)${NC}"

# 4. Final Status
cd "$SCRIPT_DIR"
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   System Started Successfully!   ${NC}"
echo -e "${GREEN}========================================${NC}"
echo "Backend PID  : $BACKEND_PID"
echo "Frontend PID : $FRONTEND_PID"
echo "Backend Log  : $SCRIPT_DIR/backend.log"
echo "Frontend Log : $SCRIPT_DIR/frontend.log"
echo ""
echo "Frontend URL : http://localhost:5173"
echo "Backend Docs : http://localhost:8000/docs"
echo -e "${GREEN}========================================${NC}"
