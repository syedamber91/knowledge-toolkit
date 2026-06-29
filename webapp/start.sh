#!/usr/bin/env bash
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "Starting backend…"
cd "$ROOT/backend"
[ ! -d .venv ] && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
source .venv/bin/activate
python seed.py 2>/dev/null || true
uvicorn main:app --port 8000 --reload &
BACKEND_PID=$!

echo "Starting frontend…"
cd "$ROOT/frontend"
[ ! -d node_modules ] && npm install
npm run dev &
FRONTEND_PID=$!

echo ""
echo "  Backend:  http://localhost:8000"
echo "  Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl-C to stop both servers."

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT TERM
wait
