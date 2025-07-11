#!/bin/bash
# Script d'exécution des tests pour la synchronisation Copper-Mailchimp

echo "🚀 Début des tests de synchronisation Copper-Mailchimp"
echo "=================================================="

# Vérifier que pytest est installé
if ! command -v pytest &> /dev/null; then
    echo "❌ pytest n'est pas installé. Installation en cours..."
    pip install -r requirements.txt
fi

# Créer le répertoire de rapports s'il n'existe pas
mkdir -p test_reports

# Fonction pour exécuter un type de test
run_test_suite() {
    local test_name=$1
    local test_path=$2
    local options=$3
    
    echo ""
    echo "🧪 Exécution des tests : $test_name"
    echo "----------------------------------------"
    
    pytest $test_path $options --html=test_reports/${test_name}_report.html --self-contained-html
    
    if [ $? -eq 0 ]; then
        echo "✅ Tests $test_name : RÉUSSIS"
    else
        echo "❌ Tests $test_name : ÉCHOUÉS"
        return 1
    fi
}

# Variables pour les options
BASIC_OPTIONS="-v --tb=short"
COVERAGE_OPTIONS="--cov=sync --cov-report=html:test_reports/coverage_html --cov-report=term-missing"
PERFORMANCE_OPTIONS="-m performance --durations=10"
INTEGRATION_OPTIONS="-m integration --run-integration"

# Menu interactif
if [ "$1" == "" ]; then
    echo "Choisissez le type de tests à exécuter :"
    echo "1) Tests complets (tous les tests)"
    echo "2) Tests unitaires seulement"
    echo "3) Tests d'API seulement"
    echo "4) Tests de performance"
    echo "5) Tests d'intégration"
    echo "6) Tests avec couverture de code"
    echo "7) Tests rapides (sans performance/intégration)"
    echo "8) Tests par fichier spécifique"
    echo "9) Tests en mode verbose avec debug"
    
    read -p "Entrez votre choix (1-9): " choice
else
    choice=$1
fi

case $choice in
    1)
        echo "🎯 Exécution de TOUS les tests"
        run_test_suite "complets" "tests/" "$BASIC_OPTIONS $COVERAGE_OPTIONS --run-integration --run-slow"
        ;;
    2)
        echo "🎯 Exécution des tests unitaires"
        run_test_suite "unitaires" "tests/test_utils.py" "$BASIC_OPTIONS $COVERAGE_OPTIONS"
        ;;
    3)
        echo "🎯 Exécution des tests d'API"
        run_test_suite "api" "tests/test_api.py" "$BASIC_OPTIONS $COVERAGE_OPTIONS"
        ;;
    4)
        echo "🎯 Exécution des tests de performance"
        run_test_suite "performance" "tests/test_performance.py" "$PERFORMANCE_OPTIONS --run-slow"
        ;;
    5)
        echo "🎯 Exécution des tests d'intégration"
        run_test_suite "integration" "tests/test_integration.py" "$INTEGRATION_OPTIONS"
        ;;
    6)
        echo "🎯 Exécution avec couverture de code détaillée"
        run_test_suite "couverture" "tests/" "$BASIC_OPTIONS $COVERAGE_OPTIONS --cov-fail-under=80"
        ;;
    7)
        echo "🎯 Exécution des tests rapides"
        run_test_suite "rapides" "tests/" "$BASIC_OPTIONS -m \"not slow and not integration\""
        ;;
    8)
        echo "Tests disponibles :"
        echo "  - test_utils.py (fonctions utilitaires)"
        echo "  - test_api.py (fonctions API)"
        echo "  - test_reporting.py (système de rapport)"
        echo "  - test_performance.py (tests de performance)"
        echo "  - test_integration.py (tests d'intégration)"
        
        read -p "Entrez le nom du fichier (sans .py): " test_file
        run_test_suite "specifique" "tests/test_${test_file}.py" "$BASIC_OPTIONS $COVERAGE_OPTIONS"
        ;;
    9)
        echo "🎯 Exécution en mode debug verbose"
        run_test_suite "debug" "tests/" "$BASIC_OPTIONS --tb=long -s --log-cli-level=DEBUG"
        ;;
    *)
        echo "❌ Choix invalide. Utilisez un numéro entre 1 et 9."
        exit 1
        ;;
esac

# Résumé final
echo ""
echo "📊 Résumé des tests"
echo "==================="
echo "📁 Rapports disponibles dans : test_reports/"
echo "🌐 Rapport HTML : test_reports/*_report.html"
echo "📈 Couverture : test_reports/coverage_html/index.html"
echo ""

# Afficher les statistiques de couverture si disponibles
if [ -f "test_reports/coverage_html/index.html" ]; then
    echo "🔍 Ouverture du rapport de couverture..."
    # Décommentez la ligne suivante si vous voulez ouvrir automatiquement le rapport
    # xdg-open test_reports/coverage_html/index.html 2>/dev/null || open test_reports/coverage_html/index.html 2>/dev/null
fi

echo "✅ Tests terminés avec succès !"
