# Polis — Makefile (architecture de référence OpenClaw)
#
# Commandes disponibles :
#   make validate   → Exécute la validation complète
#   make install    → Déploie la config vers ~/.openclaw/
#   make lint       → ShellCheck + ruff + mypy (si installés)
#   make ruff       → Vérifie le code Python avec ruff
#   make typecheck  → Vérifie les types avec mypy
#   make test       → Lance les tests (si pytest installé)
#   make coverage   → Tests avec couverture
#   make dev-setup  → Crée un venv avec les outils de dev
#   make hooks      → Installe les pre-commit hooks git
#   make help       → Affiche cette aide
#   make polis      → Affiche les commandes Polis CLI disponibles

ROOT_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
VENV      ?= $(ROOT_DIR).venv

.PHONY: validate install lint ruff typecheck test coverage dev-setup hooks help polis

validate:
	@echo "=== Validation OpenClaw ==="
	@bash "$(ROOT_DIR)scripts/validate.sh"

install:
	@bash "$(ROOT_DIR)scripts/install.sh"

lint: ruff typecheck
	@echo "=== ShellCheck ==="
	@if command -v shellcheck >/dev/null 2>&1; then \
		shellcheck "$(ROOT_DIR)scripts/"*.sh && echo "✅ Tous les scripts sont OK"; \
	else \
		echo "⚠ shellcheck non installé. Installer avec : apt install shellcheck"; \
	fi

ruff:
	@echo "=== ruff ==="
	@if command -v ruff >/dev/null 2>&1; then \
		ruff check polis/ tests/ && ruff format --check polis/ tests/ && echo "✅ ruff OK"; \
	else \
		echo "⚠ ruff non installé. Lancer : make dev-setup"; \
	fi

typecheck:
	@echo "=== mypy ==="
	@if command -v mypy >/dev/null 2>&1; then \
		mypy polis/eventbus.py polis/polis.py && echo "✅ mypy OK"; \
	else \
		echo "⚠ mypy non installé. Lancer : make dev-setup"; \
	fi

test:
	@echo "=== Tests ==="
	@if command -v pytest >/dev/null 2>&1; then \
		python3 -m pytest tests/ -v; \
	elif [ -f "$(VENV)/bin/pytest" ]; then \
		"$(VENV)/bin/pytest" tests/ -v; \
	else \
		echo "⚠ pytest non installé. Lancer : make dev-setup"; \
	fi

coverage:
	@echo "=== Tests avec couverture ==="
	@python3 -m coverage run --rcfile=.coveragerc -m pytest tests/ -v && \
	 python3 -m coverage report --rcfile=.coveragerc

dev-setup:
	@echo "=== Création du venv ==="
	@python3 -m venv "$(VENV)"
	@"$(VENV)/bin/pip" install --quiet ruff mypy pytest coverage
	@echo "✅ Dev setup terminé. Utiliser : source $(VENV)/bin/activate"

hooks:
	@echo "=== Installation des pre-commit hooks ==="
	@git config core.hooksPath "$(ROOT_DIR).githooks"
	@echo "✅ Hooks installés depuis .githooks/pre-commit"

help:
	@echo "OpenClaw — Commandes disponibles"
	@echo ""
	@echo "  make validate   Exécute la validation complète (validate.sh)"
	@echo "  make install    Déploie l'instance vers ~/.openclaw/"
	@echo "  make lint       ShellCheck + ruff + mypy"
	@echo "  make ruff       Vérifie le code Python avec ruff"
	@echo "  make typecheck  Vérifie les types avec mypy"
	@echo "  make test       Lance les tests (si pytest installé)"
	@echo "  make coverage   Tests avec couverture (seuil 70%)"
	@echo "  make dev-setup  Crée un venv avec les outils de dev"
	@echo "  make hooks      Installe les pre-commit hooks git"
	@echo "  make help       Affiche cette aide"

.PHONY: polis

polis:
	@echo "Polis CLI — Commandes disponibles"
	@echo ""
	@echo "  polis check constitution    Vérifie la cohérence de la constitution"
	@echo "  polis check agents          Vérifie les workspaces des agents"
	@echo "  polis check config          Valide openclaw.json"
	@echo "  polis guardrail simulate    Simule une décision Guardrail"
	@echo "  polis demo leviathan        Scénario de démonstration LEVIATHAN"
	@echo "  polis test run              Lance les tests"
	@echo ""
	@echo "  CLI en cours de développement."
