# floating-agent — Makefile
# Architecture: native PySide6 overlay + Python agent core (single process)
# Extends conventions from Forge-Stack-Workshop/base-makefile

.DEFAULT_GOAL := help

PYTHON        := python3
PIP           := $(PYTHON) -m pip
PACKAGE       := floating_agent

# ──────────────────────────────────────────────────────────────────────────────

.PHONY: help
help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}'

# ──────────────────────────────────────────────────────────────────────────────
# Setup & Install
# ──────────────────────────────────────────────────────────────────────────────

.PHONY: install
install: ## Install python deps + pre-commit hooks
	$(PIP) install -e ".[dev]"
	pre-commit install

# ──────────────────────────────────────────────────────────────────────────────
# Development
# ──────────────────────────────────────────────────────────────────────────────

.PHONY: dev
dev: ## Launch the native PySide6 overlay
	$(PYTHON) -m $(PACKAGE)

.PHONY: serve
serve: ## (optional) Run the FastAPI HTTP layer on 127.0.0.1:34001
	uvicorn $(PACKAGE).main:app --reload --host 127.0.0.1 --port 34001

# ──────────────────────────────────────────────────────────────────────────────
# Test (Docker — chrysa standard)
# ──────────────────────────────────────────────────────────────────────────────

.PHONY: test
test: ## Run tests in Docker
	docker build -f Dockerfile.test -t floating-agent-test . && docker run --rm floating-agent-test

.PHONY: docker-test
docker-test: test ## Alias for CI-compatible docker-based test

# ──────────────────────────────────────────────────────────────────────────────
# Lint, Format, Typecheck
# ──────────────────────────────────────────────────────────────────────────────

.PHONY: lint
lint: ## Lint with Ruff
	ruff check $(PACKAGE) tests

.PHONY: format
format: ## Format with Ruff
	ruff format $(PACKAGE) tests
	ruff check --fix $(PACKAGE) tests

.PHONY: typecheck
typecheck: ## Type-check with mypy
	mypy $(PACKAGE)

# ──────────────────────────────────────────────────────────────────────────────
# Build & Package (PyInstaller — PR8)
# ──────────────────────────────────────────────────────────────────────────────

.PHONY: build
build: ## Package a standalone binary for the current OS (PyInstaller)
	pyinstaller --noconfirm packaging/floating-agent.spec

# ──────────────────────────────────────────────────────────────────────────────
# Quality
# ──────────────────────────────────────────────────────────────────────────────

.PHONY: pre-commit
pre-commit: ## Run all pre-commit hooks
	pre-commit run --all-files

.PHONY: ci
ci: lint typecheck test ## Run all CI checks locally

quality-gate-baseline: ## Record baseline metrics for regression detection
	@python3 scripts/quality_gate.py baseline

quality-gate-verify: ## Verify no regression since baseline
	@python3 scripts/quality_gate.py verify

# ──────────────────────────────────────────────────────────────────────────────
# Clean
# ──────────────────────────────────────────────────────────────────────────────

.PHONY: clean
clean: ## Remove build artifacts and caches
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf dist/ build/ htmlcov/ coverage.xml reports/
	@echo "Clean complete"
