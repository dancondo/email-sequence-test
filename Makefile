ALEMBIC = docker compose exec -e PYTHONPATH=/app backend alembic

# --- Docker ---

up:
	docker compose up

up-build:
	docker compose up --build

up-ngrok:
	docker compose -f docker-compose.yml -f docker-compose.ngrok.yml up

up-ngrok-build:
	docker compose -f docker-compose.yml -f docker-compose.ngrok.yml up --build

down:
	docker compose down

# --- Migrations ---

migration:
	@read -p "Migration message: " msg; \
	$(ALEMBIC) revision --autogenerate -m "$$msg"

migrate:
	$(ALEMBIC) upgrade head

migrate-down:
	$(ALEMBIC) downgrade -1

migrate-reset:
	$(ALEMBIC) downgrade base

migrate-history:
	$(ALEMBIC) history --verbose
