.PHONY: dev down

dev:
	@echo "Starting local development environment..."
	@docker-compose up --build -d
	@echo "Services are running. API on http://localhost:8000, Dashboard on http://localhost:8501"

down:
	@echo "Stopping local development environment..."
	@docker-compose down
	@echo "Services stopped." 