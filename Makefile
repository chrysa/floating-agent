# makefile-tier: lib
# floating-agent — Makefile
# Architecture: native PySide6 overlay + Python agent core (single process)
# Extends conventions from Forge-Stack-Workshop/base-makefile

.DEFAULT_GOAL := help

UV            := uv
PYTHON        := $(UV) run python
PACKAGE       := floating_agent
XDG_DATA_HOME ?= $(HOME)/.local/share
UV_PROJECT_ENVIRONMENT ?= $(XDG_DATA_HOME)/floating-agent/venv
export UV_PROJECT_ENVIRONMENT

# ──────────────────────────────────────────────────────────────────────────────

.PHONY: help
help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}'

# ──────────────────────────────────────────────────────────────────────────────
# Setup & Install
# ──────────────────────────────────────────────────────────────────────────────

.PHONY: install
install: ## Install locked runtime dependencies with uv
	@$(UV) sync --frozen

.PHONY: install-dev
install-dev: ## Install development dependencies + pre-commit hooks
	@$(UV) sync --frozen --all-extras
	@$(UV) run pre-commit install

# ──────────────────────────────────────────────────────────────────────────────
# Development
# ──────────────────────────────────────────────────────────────────────────────

.PHONY: dev
dev: ## Launch the native PySide6 overlay
	@$(PYTHON) -m $(PACKAGE)

.PHONY: serve
serve: ## (optional) Run the FastAPI HTTP layer on 127.0.0.1:34001
	@$(UV) run uvicorn $(PACKAGE).main:app --reload --host 127.0.0.1 --port 34001

# ──────────────────────────────────────────────────────────────────────────────
# Test (Docker — chrysa standard)
# ──────────────────────────────────────────────────────────────────────────────

.PHONY: test
test: ## Run tests in Docker
	@docker build -f Dockerfile.test -t floating-agent-test . && docker run --rm floating-agent-test

.PHONY: docker-test
docker-test: test ## Alias for CI-compatible docker-based test

.PHONY: test-cov
test-cov: ## Run tests with coverage report
	@$(UV) run pytest --cov=$(PACKAGE) --cov-report=term-missing --cov-report=xml

# ──────────────────────────────────────────────────────────────────────────────
# Lint, Format, Typecheck
# ──────────────────────────────────────────────────────────────────────────────

.PHONY: lint
lint: ## Lint with Ruff
	@$(UV) run ruff check $(PACKAGE) tests

.PHONY: format
format: ## Format with Ruff
	@$(UV) run ruff format $(PACKAGE) tests
	@$(UV) run ruff check --fix $(PACKAGE) tests

.PHONY: format-check
format-check: ## Check formatting with Ruff
	@$(UV) run ruff format --check $(PACKAGE) tests

.PHONY: typecheck
typecheck: ## Type-check with mypy
	@$(UV) run mypy $(PACKAGE)

# ──────────────────────────────────────────────────────────────────────────────
# Build & Package (PyInstaller — PR8)
# ──────────────────────────────────────────────────────────────────────────────

.PHONY: build
build: ## Package a standalone binary for the current OS (PyInstaller)
	@$(UV) run pyinstaller --noconfirm packaging/floating-agent.spec

# ──────────────────────────────────────────────────────────────────────────────
# Quality
# ──────────────────────────────────────────────────────────────────────────────

.PHONY: pre-commit
pre-commit: ## Run all pre-commit hooks
	@$(UV) run pre-commit run --all-files

.PHONY: ci
ci: lint format-check typecheck test ## Run all CI checks locally

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
