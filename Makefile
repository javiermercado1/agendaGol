PHONY := start stop logs init

.PHONY: start stop logs init


start:
	chmod +x run_local.sh
	./run_local.sh

stop:
	@echo "Stopping services..."
	@if [ -f .auth.pid ]; then kill $(cat .auth.pid) || true; fi
	@if [ -f .roles.pid ]; then kill $(cat .roles.pid) || true; fi
	@if [ -f .fields.pid ]; then kill $(cat .fields.pid) || true; fi
	@if [ -f .reservations.pid ]; then kill $(cat .reservations.pid) || true; fi
	@if [ -f .dashboard.pid ]; then kill $(cat .dashboard.pid) || true; fi
	@rm -f .auth.pid .roles.pid .fields.pid .reservations.pid .dashboard.pid
	@echo "Killing any remaining uvicorn processes..."
	@pkill -f "uvicorn app.main:app" || true

logs:
	@mkdir -p logs
	@echo "Tailing logs (ctrl+C to exit)"
	@if ls logs/*.log >/dev/null 2>&1; then \
		tail -f logs/*.log; \
	else \
		echo "No logs found in ./logs/"; exit 1; \
	fi


status:
	@echo "Service PIDs and process info:"
	@for f in .auth.pid .roles.pid .fields.pid .reservations.pid .dashboard.pid; do \
		if [ -f $$f ]; then \
			pid=$$(cat $$f); \
			echo "$$f -> PID=$$pid"; \
			ps -p $$pid -o pid,comm || ps -p $$pid -o pid,command || true; \
		else \
			echo "$$f not found"; \
		fi; \
	done
	@echo "\nListening ports (8000-8004):"
	@for port in 8000 8001 8002 8003 8004; do \
		if command -v lsof >/dev/null 2>&1; then \
			lsof -iTCP:$$port -sTCP:LISTEN -Pn || echo "port $$port: not listening"; \
		else \
			echo "lsof not available; try: ss or netstat to inspect port $$port"; \
		fi; \
	done


init:
	@echo "Initializing sqlite databases for all services..."
	@# Ensure Python packages are installed first
	@if command -v pip3 >/dev/null 2>&1; then \
		pip3 install -r requirements.txt; \
	elif command -v pip >/dev/null 2>&1; then \
		pip install -r requirements.txt; \
	else \
		echo "No pip found. Please install Python 3 and pip."; exit 1; \
	fi
	@if command -v python3 >/dev/null 2>&1; then \
		PYTHONPATH="$$(pwd)/auth_service" python3 auth_service/app/init_db.py; \
		PYTHONPATH="$$(pwd)/roles_service" python3 roles_service/app/init_db.py; \
		PYTHONPATH="$$(pwd)/fields_service" python3 fields_service/app/init_db.py; \
		PYTHONPATH="$$(pwd)/reservations_service" python3 reservations_service/app/init_db.py; \
	elif command -v python >/dev/null 2>&1; then \
		PYTHONPATH="$$(pwd)/auth_service" python auth_service/app/init_db.py; \
		PYTHONPATH="$$(pwd)/roles_service" python roles_service/app/init_db.py; \
		PYTHONPATH="$$(pwd)/fields_service" python fields_service/app/init_db.py; \
		PYTHONPATH="$$(pwd)/reservations_service" python reservations_service/app/init_db.py; \
	else \
		echo "No python interpreter found. Please install Python 3."; exit 1; \
	fi
	@echo "Initialization complete."
