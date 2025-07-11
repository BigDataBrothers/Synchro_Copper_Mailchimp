# Makefile pour la synchronisation Copper-Mailchimp
# Utilise Python 3 et pytest pour les tests

.PHONY: help install test test-unit test-api test-integration test-performance test-coverage clean lint format check-deps

# Variables
PYTHON = python3
PIP = pip3
PYTEST = pytest
PROJECT_NAME = copper_mailchimp_sync
VENV_NAME = venv_test

# Aide par défaut
help:
	@echo "🚀 Makefile pour $(PROJECT_NAME)"
	@echo "================================="
	@echo ""
	@echo "Commandes disponibles :"
	@echo "  install          - Installer les dépendances"
	@echo "  test             - Exécuter tous les tests"
	@echo "  test-unit        - Exécuter les tests unitaires"
	@echo "  test-api         - Exécuter les tests d'API"
	@echo "  test-integration - Exécuter les tests d'intégration"
	@echo "  test-performance - Exécuter les tests de performance"
	@echo "  test-coverage    - Exécuter les tests avec couverture"
	@echo "  test-fast        - Exécuter les tests rapides"
	@echo "  lint             - Vérifier la syntaxe du code"
	@echo "  format           - Formater le code"
	@echo "  clean            - Nettoyer les fichiers temporaires"
	@echo "  check-deps       - Vérifier les dépendances"
	@echo "  setup-venv       - Créer un environnement virtuel"
	@echo "  run-sync         - Exécuter la synchronisation"
	@echo ""

# Installation des dépendances
install:
	@echo "📦 Installation des dépendances..."
	$(PIP) install -r requirements.txt
	@echo "✅ Installation terminée"

# Vérification des dépendances
check-deps:
	@echo "🔍 Vérification des dépendances..."
	@$(PYTHON) -c "import requests; print('✅ requests OK')" || echo "❌ requests manquant"
	@$(PYTHON) -c "import pytest; print('✅ pytest OK')" || echo "❌ pytest manquant"
	@$(PYTHON) -c "import responses; print('✅ responses OK')" || echo "❌ responses manquant"
	@$(PYTHON) -c "from dotenv import load_dotenv; print('✅ python-dotenv OK')" || echo "❌ python-dotenv manquant"

# Environnement virtuel
setup-venv:
	@echo "🏗️ Création de l'environnement virtuel..."
	$(PYTHON) -m venv $(VENV_NAME)
	@echo "✅ Environnement virtuel créé : $(VENV_NAME)"
	@echo "💡 Pour l'activer : source $(VENV_NAME)/bin/activate"

# Tests complets
test:
	@echo "🧪 Exécution de tous les tests..."
	@mkdir -p test_reports
	$(PYTEST) tests/ -v --tb=short --html=test_reports/full_report.html --self-contained-html
	@echo "✅ Tests terminés - Rapport : test_reports/full_report.html"

# Tests unitaires
test-unit:
	@echo "🧪 Exécution des tests unitaires..."
	@mkdir -p test_reports
	$(PYTEST) tests/test_utils.py -v --html=test_reports/unit_report.html --self-contained-html
	@echo "✅ Tests unitaires terminés"

# Tests d'API
test-api:
	@echo "🧪 Exécution des tests d'API..."
	@mkdir -p test_reports
	$(PYTEST) tests/test_api.py -v --html=test_reports/api_report.html --self-contained-html
	@echo "✅ Tests d'API terminés"

# Tests d'intégration
test-integration:
	@echo "🧪 Exécution des tests d'intégration..."
	@mkdir -p test_reports
	$(PYTEST) tests/test_integration.py -v --run-integration --html=test_reports/integration_report.html --self-contained-html
	@echo "✅ Tests d'intégration terminés"

# Tests de performance
test-performance:
	@echo "🧪 Exécution des tests de performance..."
	@mkdir -p test_reports
	$(PYTEST) tests/test_performance.py -v --run-slow --durations=10 --html=test_reports/performance_report.html --self-contained-html
	@echo "✅ Tests de performance terminés"

# Tests avec couverture
test-coverage:
	@echo "🧪 Exécution des tests avec couverture..."
	@mkdir -p test_reports
	$(PYTEST) tests/ -v --cov=sync --cov-report=html:test_reports/coverage_html --cov-report=term-missing --cov-fail-under=80
	@echo "✅ Tests avec couverture terminés"
	@echo "📊 Rapport de couverture : test_reports/coverage_html/index.html"

# Tests rapides (sans performance/intégration)
test-fast:
	@echo "🧪 Exécution des tests rapides..."
	@mkdir -p test_reports
	$(PYTEST) tests/ -v -m "not slow and not integration" --html=test_reports/fast_report.html --self-contained-html
	@echo "✅ Tests rapides terminés"

# Vérification de la syntaxe (si pyflakes est installé)
lint:
	@echo "🔍 Vérification de la syntaxe..."
	@if command -v pyflakes >/dev/null 2>&1; then \
		pyflakes sync.py tests/; \
		echo "✅ Vérification terminée"; \
	else \
		echo "💡 pyflakes non installé, vérification basique..."; \
		$(PYTHON) -m py_compile sync.py; \
		echo "✅ Compilation OK"; \
	fi

# Formatage du code (si black est installé)
format:
	@echo "🎨 Formatage du code..."
	@if command -v black >/dev/null 2>&1; then \
		black sync.py tests/; \
		echo "✅ Formatage terminé"; \
	else \
		echo "💡 black non installé, formatage ignoré"; \
	fi

# Nettoyage des fichiers temporaires
clean:
	@echo "🧹 Nettoyage des fichiers temporaires..."
	@rm -rf __pycache__/
	@rm -rf tests/__pycache__/
	@rm -rf .pytest_cache/
	@rm -rf test_reports/
	@rm -rf .coverage
	@rm -rf htmlcov/
	@rm -f *.pyc
	@rm -f tests/*.pyc
	@rm -f sync_log_*.txt
	@rm -f import_report_*.txt
	@echo "✅ Nettoyage terminé"

# Exécution de la synchronisation
run-sync:
	@echo "🔄 Exécution de la synchronisation..."
	@if [ -f .env ]; then \
		$(PYTHON) sync.py; \
	else \
		echo "❌ Fichier .env non trouvé"; \
		echo "💡 Créez un fichier .env avec vos clés API"; \
	fi

# Tests avec rapport détaillé
test-detailed:
	@echo "🧪 Exécution des tests avec rapport détaillé..."
	@mkdir -p test_reports
	$(PYTEST) tests/ -v --tb=long --html=test_reports/detailed_report.html --self-contained-html --cov=sync --cov-report=html:test_reports/coverage_html
	@echo "✅ Tests détaillés terminés"
	@echo "📊 Rapports disponibles :"
	@echo "   - Tests : test_reports/detailed_report.html"
	@echo "   - Couverture : test_reports/coverage_html/index.html"

# Vérification complète (tests + lint + couverture)
check-all: lint test-coverage
	@echo "✅ Vérification complète terminée"

# Installation des outils de développement
install-dev:
	@echo "📦 Installation des outils de développement..."
	$(PIP) install black pyflakes pytest-html pytest-cov pytest-mock responses
	@echo "✅ Outils de développement installés"

# Affichage des statistiques de test
test-stats:
	@echo "📊 Statistiques des tests..."
	@echo "Nombre de fichiers de test : $$(find tests/ -name 'test_*.py' | wc -l)"
	@echo "Nombre de tests : $$(grep -r 'def test_' tests/ | wc -l)"
	@echo "Taille du code principal : $$(wc -l sync.py | cut -d' ' -f1) lignes"
	@echo "Taille des tests : $$(find tests/ -name '*.py' -exec wc -l {} + | tail -1 | cut -d' ' -f1) lignes"
