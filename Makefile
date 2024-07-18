.PHONY: run-cuda
up-cpu: ## Run cpu version
	@docker compose -f docker-compose.cpu.yml up -d

.PHONY: down-cpu
down-cpu: ## down cpu version
	@docker compose -f docker-compose.cpu.yml down

.PHONY: up
up: ## Run cuda version
	@docker compose up -d

.PHONY: down
down: ## Run cuda version
	@docker compose down