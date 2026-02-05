.PHONY: dev build stop clean test

# Start everything in the background
dev:
	docker-compose up -d

# Build or Rebuild services
build:
	docker-compose build

# View logs for all services
logs:
	docker-compose logs -f

# Stop all services
stop:
	docker-compose down

# Run a quick test curl to the gateway
test-request:
	curl -X POST http://localhost:8000/v1/llm/respond \
	-H "Content-Type: application/json" \
	-d '{"prompt": "Hello world"}'