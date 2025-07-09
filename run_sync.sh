#!/bin/bash

# Script de lancement de la synchronisation Copper-Mailchimp
echo "=================================================="
echo "  SYNCHRONISATION COPPER ↔ MAILCHIMP"
echo "=================================================="
echo

# Vérification du fichier .env
if [ ! -f .env ]; then
  echo "❌ Erreur: Fichier .env non trouvé"
  echo "   Veuillez créer un fichier .env avec les informations d'API requises."
  echo "   Pour plus d'informations, consultez DOCUMENTATION.md"
  exit 1
fi

# Vérification de l'installation de Python
if ! command -v python3 &> /dev/null; then
  echo "❌ Erreur: Python n'est pas installé ou n'est pas dans le PATH"
  echo "   Veuillez installer Python 3.6 ou supérieur."
  exit 1
fi

# Lancement du programme
echo "🔄 Démarrage de la synchronisation optimisée..."
echo "   (Cette opération peut prendre quelques minutes selon la taille de vos données)"
echo

python3 sync.py

# Vérification du code de retour
if [ $? -eq 0 ]; then
  echo
  echo "✅ Synchronisation terminée avec succès!"
  
  # Recherche du dernier log généré
  LATEST_LOG=$(ls -t sync_log_*.txt 2>/dev/null | head -1)
  if [ -n "$LATEST_LOG" ]; then
    echo "   Log détaillé disponible: $LATEST_LOG"
    echo
    echo "   Pour consulter le log complet, exécutez:"
    echo "   cat $LATEST_LOG"
  fi
  
  echo
  echo "📚 Pour plus d'informations sur la lecture des logs,"
  echo "   consultez le fichier GUIDE_RAPIDE.md"
else
  echo
  echo "❌ Une erreur s'est produite pendant la synchronisation."
  echo "   Consultez les fichiers de log pour plus de détails."
  
  # Recherche du dernier log généré
  LATEST_LOG=$(ls -t sync_log_*.txt | head -1)
  if [ -n "$LATEST_LOG" ]; then
    echo "   Log d'erreur: $LATEST_LOG"
  fi
fi

echo
echo "=================================================="
