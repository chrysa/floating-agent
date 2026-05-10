# floating-agent — Makefile
# Architecture: Electron + React UI + Python daemon
# Extends conventions from Forge-Stack-Workshop/base-makefile

.DEFAULT_GOAL := help

PYTHON        := python3
NODE          := node
NPM           := npm
DC            := docker compose

DAEMON_DIR    := daemon
UI_DIR        := ui
ELECTRON_DIR  := electron

# ──────────────────────────────────────────────────────────────────────────────

.PHONY: help
help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}'

# ──────────────────────────────────────────────────────────────────────────────
# Setup & Install
# ──────────────────────────────────────────────────────────────────────────────

.PHONY: install
install: install-electron install-ui install-daemon pre-commit-install ## Install all dependencies

.PHONY: install-electron
install-electron: ## Install Electron dependencies
	$(NPM) install --prefix $(ELECTRON_DIR)

.PHONY: install-ui
install-ui: ## Install UI (React) dependencies
	$(NPM) install --prefix $(UI_DIR)

.PHONY: install-daemon
install-daemon: ## Install Python daemon dependencies
	$(PYTHON) -m pip install -e "$(DAEMON_DIR)[dev]"

.PHONY: pre-commit-install
pre-commit-install: ## Install pre-commit hooks
	pre-commit install

# ──────────────────────────────────────────────────────────────────────────────
# Development
# ──────────────────────────────────────────────────────────────────────────────

.PHONY: dev
dev: ## Start Electron in development mode (hot reload)
	$(NPM) run dev --prefix $(ELECTRON_DIR)

.PHONY: dev-ui
dev-ui: ## Start React UI dev server only (browser)
	$(NPM) run dev --prefix $(UI_DIR)

.PHONY: dev-daemon
dev-daemon: ## Start Python daemon in dev mode
	cd $(DAEMON_DIR) && uvicorn floating_agent.main:app --reload --host 127.0.0.1 --port 34001

# ──────────────────────────────────────────────────────────────────────────────
# Test
# ──────────────────────────────────────────────────────────────────────────────

.PHONY: test
test: test-ui test-daemon ## Run all tests

.PHONY: test-ui
test-ui: ## Run UI tests (Vitest)
	$(NPM) run test --prefix $(UI_DIR)

.PHONY: test-daemon
test-daemon: ## Run daemon tests (pytest)
	cd $(DAEMON_DIR) && pytest

.PHONY: test-cov
test-cov: ## Run daemon tests with coverage
	cd $(DAEMON_DIR) && pytest --cov=floating_agent --cov-report=term-missing --cov-report=xml --cov-fail-under=85

# ──────────────────────────────────────────────────────────────────────────────
# Lint & Format
# ──────────────────────────────────────────────────────────────────────────────

.PHONY: lint
lint: lint-ui lint-daemon ## Lint all code

.PHONY: lint-ui
lint-ui: ## Lint UI code (ESLint)
	$(NPM) run lint --prefix $(UI_DIR)
	$(NPM) run lint --prefix $(ELECTRON_DIR)

.PHONY: lint-daemon
lint-daemon: ## Lint daemon code (Ruff)
	ruff check $(DAEMON_DIR)

.PHONY: format
format: format-ui format-daemon ## Format all code

.PHONY: format-ui
format-ui: ## Format UI code (Prettier)
	$(NPM) run format --prefix $(UI_DIR)

.PHONY: format-daemon
format-daemon: ## Format daemon code (Ruff)
	ruff format $(DAEMON_DIR)
	ruff check --fix $(DAEMON_DIR)

.PHONY: typecheck
typecheck: ## Run type checking (tsc + mypy)
	$(NPM) run typecheck --prefix $(UI_DIR)
	$(NPM) run typecheck --prefix $(ELECTRON_DIR)
	cd $(DAEMON_DIR) && mypy floating_agent

# ──────────────────────────────────────────────────────────────────────────────
# Build & Package
# ──────────────────────────────────────────────────────────────────────────────

.PHONY: build
build: build-ui build-electron ## Build for production

.PHONY: build-ui
build-ui: ## Build React UI
	$(NPM) run build --prefix $(UI_DIR)

.PHONY: build-electron
build-electron: ## Build Electron main process
	$(NPM) run build --prefix $(ELECTRON_DIR)

.PHONY: package
package: build ## Package distributable for current OS
	$(NPM) run package --prefix $(ELECTRON_DIR)

.PHONY: package-linux
package-linux: build ## Package for Linux (AppImage + deb)
	$(NPM) run package:linux --prefix $(ELECTRON_DIR)

.PHONY: package-win
package-win: build ## Package for Windows (NSIS installer)
	$(NPM) run package:win --prefix $(ELECTRON_DIR)

# ──────────────────────────────────────────────────────────────────────────────
# Quality
# ──────────────────────────────────────────────────────────────────────────────

.PHONY: pre-commit
pre-commit: ## Run all pre-commit hooks
	pre-commit run --all-files

.PHONY: ci
ci: lint typecheck test ## Run all CI checks locally

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
	rm -rf $(DAEMON_DIR)/dist/ $(DAEMON_DIR)/build/ $(DAEMON_DIR)/htmlcov/ $(DAEMON_DIR)/coverage.xml
	rm -rf $(ELECTRON_DIR)/dist/ $(ELECTRON_DIR)/out/
	rm -rf $(UI_DIR)/dist/
	@echo "Clean complete"

# ── Quality Gates ──────────────────────────────────────────────────────────────

quality-gate-baseline: ## Record baseline metrics for regression detection
	@python3 scripts/quality_gate.py baseline

quality-gate-verify: ## Verify no regression since baseline
	@python3 scripts/quality_gate.py verify
