COMPOSE = docker compose -f infra/docker/docker-compose.yml

.PHONY: help dev dev-stop logs clean docker-build health-check test test-api wait-api smoke-api pytest-api shell-api shell-db

help: ## Show targets
	@echo 'Usage: make [target]'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-18s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

dev: ## Start dev stack (API + Redis + Postgres)
	$(COMPOSE) up --build -d
	@echo "  API      : http://localhost:8000"
	@echo "  Docs     : http://localhost:8000/docs"
	@echo "  Metrics  : http://localhost:8000/api/metrics"
	@echo "  Postgres : localhost:5432"
	@echo "  Redis    : localhost:6379"

dev-stop: ## Stop stack (preserve volumes)
	$(COMPOSE) down

logs: ## Tail all container logs
	$(COMPOSE) logs -f

clean: ## Stop & wipe containers + volumes (DANGER)
	$(COMPOSE) down -v
	docker system prune -f

docker-build: ## Rebuild images
	$(COMPOSE) build

health-check: ## Quick API health & metrics (jq fallback)
	@echo "Health:" ; \
	curl -s http://localhost:8000/api/health | jq . 2>/dev/null || curl -s http://localhost:8000/api/health ; echo ; \
	echo "Metrics:" ; \
	curl -s http://localhost:8000/api/metrics | head -n 50

test: test-api ## Run all tests (currently smoke tests)

test-api: wait-api smoke-api ## API smoke tests via curl (no pytest needed)

wait-api: ## Wait until API is healthy (max 60s)
	@echo "Waiting for API on :8000 ..." ; \
	for i in $$(seq 1 60); do \
	  out=$$(curl -sS --max-time 2 http://localhost:8000/api/health || true); \
	  echo "$$out" | grep -q '"status":"ok"' && { echo "API is healthy"; exit 0; }; \
	  sleep 1; \
	done; \
	echo "API did not become healthy in time"; exit 1

smoke-api: ## Signup/Login/Chat/History/Stats happy-path check
	@set -euo pipefail ; set -o pipefail ; \
	echo "== Health" ; \
	curl -fsS http://localhost:8000/api/health >/dev/null && echo "OK" ; \
	EMAIL="make+$$(( $$(date +%s) ))@example.com" ; PASS="pass" ; \
	echo "== Signup $$EMAIL" ; \
	curl -fsS -w '\nHTTP:%{http_code}\n' -X POST http://localhost:8000/api/v1/auth/signup \
	  -H 'Content-Type: application/json' \
	  -d "$$(jq -n --arg e $$EMAIL --arg p $$PASS '{email:$$e,password:$$p}')" | tee /tmp/signup.out ; \
	STATUS=$$(tail -n1 /tmp/signup.out | sed 's/HTTP://'); \
	if [ "$$STATUS" != "200" ] && [ "$$STATUS" != "409" ]; then echo "Signup failed HTTP $$STATUS"; exit 1; fi ; \
	echo "== Login" ; \
	TOKEN=$$(curl -fsS -X POST http://localhost:8000/api/v1/auth/login \
	  -H 'Content-Type: application/json' \
	  -d "$$(jq -n --arg e $$EMAIL --arg p $$PASS '{email:$$e,password:$$p}')" | jq -r '.access_token') ; \
	test -n "$$TOKEN" ; echo "Token prefix: $${TOKEN:0:20}..." ; \
	echo "== Chat" ; \
	curl -fsS -X POST http://localhost:8000/api/v1/chat/message \
	  -H "Authorization: Bearer $$TOKEN" -H 'Content-Type: application/json' \
	  -d '{"message":"hello from make"}' >/dev/null ; \
	echo "== History" ; \
	curl -fsS "http://localhost:8000/api/v1/chat/history?limit=2" \
	  -H "Authorization: Bearer $$TOKEN" | jq '. | length' 2>/dev/null | grep -qE '^[12]$$' || (echo "history len unexpected"; exit 1) ; \
	echo "== Metrics (snippet)" ; \
	curl -fsS http://localhost:8000/api/metrics | grep -E 'chat_messages_total|chat_request_latency_seconds_count' | head -n 5 || true ; \
	echo "Smoke tests: OK"

pytest-api: ## OPTIONAL: run pytest inside API container if tests exist
	$(COMPOSE) exec -T api sh -lc 'if [ -d apps/api/tests ]; then pytest -q apps/api/tests -q --disable-warnings; else echo "No apps/api/tests found, skipping"; fi'

shell-api: ## Shell into API container
	$(COMPOSE) exec api sh

shell-db: ## psql shell
	$(COMPOSE) exec postgres psql -U vakta -d vakta
