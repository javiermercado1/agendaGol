#!/usr/bin/env bash
set -euo pipefail

# Simple local runner for all services using SQLite
# Usage: chmod +x run_local.sh && ./run_local.sh

echo "Installing Python requirements..."
if command -v pip3 >/dev/null 2>&1; then
	pip3 install -r requirements.txt
elif command -v pip >/dev/null 2>&1; then
	pip install -r requirements.txt
else
	echo "No pip found. Please install Python 3 and pip." >&2
	exit 1
fi

echo "Initializing sqlite databases..."
if command -v python3 >/dev/null 2>&1; then
    PYTHONPATH="$PWD/auth_service" python3 auth_service/app/init_db.py
    PYTHONPATH="$PWD/roles_service" python3 roles_service/app/init_db.py
    PYTHONPATH="$PWD/fields_service" python3 fields_service/app/init_db.py
    PYTHONPATH="$PWD/reservations_service" python3 reservations_service/app/init_db.py
elif command -v python >/dev/null 2>&1; then
    PYTHONPATH="$PWD/auth_service" python auth_service/app/init_db.py
    PYTHONPATH="$PWD/roles_service" python roles_service/app/init_db.py
    PYTHONPATH="$PWD/fields_service" python fields_service/app/init_db.py
    PYTHONPATH="$PWD/reservations_service" python reservations_service/app/init_db.py
else
    echo "No python interpreter found. Please install Python 3." >&2
    exit 1
fi

echo "Starting services (they will run in background). Logs: ./logs/<service>.log"
mkdir -p logs

# Determine python executable
PYTHON_EXEC=""
if command -v python3 >/dev/null 2>&1; then
	PYTHON_EXEC=$(command -v python3)
elif command -v python >/dev/null 2>&1; then
	PYTHON_EXEC=$(command -v python)
else
	echo "No python interpreter found. Please install Python 3." >&2
	exit 1
fi

# Ensure current project root is in PYTHONPATH so packages like auth_service can be imported
export PYTHONPATH="$PWD:${PYTHONPATH:-}"

# Start each service using `python -m uvicorn` so we don't depend on uvicorn scripts in PATH
nohup "$PYTHON_EXEC" -m uvicorn app.main:app --app-dir auth_service --reload --port 8000 > logs/auth.log 2>&1 &
echo $! > .auth.pid

nohup "$PYTHON_EXEC" -m uvicorn app.main:app --app-dir roles_service --reload --port 8001 > logs/roles.log 2>&1 &
echo $! > .roles.pid

nohup "$PYTHON_EXEC" -m uvicorn app.main:app --app-dir fields_service --reload --port 8002 > logs/fields.log 2>&1 &
echo $! > .fields.pid

nohup "$PYTHON_EXEC" -m uvicorn app.main:app --app-dir reservations_service --reload --port 8003 > logs/reservations.log 2>&1 &
echo $! > .reservations.pid

nohup "$PYTHON_EXEC" -m uvicorn app.main:app --app-dir admin_dashboard --reload --port 8004 > logs/dashboard.log 2>&1 &
echo $! > .dashboard.pid

echo "All services started. Ports: 8000..8004"
echo "To stop all services run: make stop"
