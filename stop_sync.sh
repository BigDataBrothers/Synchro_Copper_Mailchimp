#!/bin/bash

echo "🛑 Arrêt et suppression complète de la synchronisation automatique"
echo "================================================================="

# 1. Arrêter tous les processus liés à la synchronisation
echo "📋 Étape 1: Arrêt des processus en cours..."
pkill -f "run_sync_cron.sh" 2>/dev/null
pkill -f "sync.py" 2>/dev/null
pkill -f "python3.*sync.py" 2>/dev/null
echo "   ✅ Processus arrêtés"

# 2. Vérifier et nettoyer le crontab utilisateur
echo "📋 Étape 2: Nettoyage du crontab utilisateur..."
if crontab -l 2>/dev/null | grep -q "run_sync_cron.sh"; then
    crontab -l | grep -v "run_sync_cron.sh" | crontab -
    echo "   ✅ Tâche cron supprimée du crontab utilisateur"
else
    echo "   ℹ️  Aucune tâche cron trouvée dans le crontab utilisateur"
fi

# 3. Vérifier le crontab root (avec sudo si disponible)
echo "📋 Étape 3: Vérification du crontab root..."
if sudo -n crontab -l 2>/dev/null | grep -q "run_sync_cron.sh"; then
    sudo crontab -l | grep -v "run_sync_cron.sh" | sudo crontab -
    echo "   ✅ Tâche cron supprimée du crontab root"
else
    echo "   ℹ️  Aucune tâche cron trouvée dans le crontab root"
fi

# 4. Supprimer les fichiers liés à l'automatisation
echo "📋 Étape 4: Suppression des fichiers d'automatisation..."
if [ -f "run_sync_cron.sh" ]; then
    rm -f "run_sync_cron.sh"
    echo "   ✅ Script run_sync_cron.sh supprimé"
else
    echo "   ℹ️  Script run_sync_cron.sh non trouvé"
fi

# 5. Optionnel: Supprimer les logs de synchronisation automatique
echo "📋 Étape 5: Nettoyage des logs (optionnel)..."
read -p "Voulez-vous supprimer les logs de synchronisation automatique (sync_cron.log) ? (o/n): " remove_logs
if [[ $remove_logs == "o" || $remove_logs == "O" ]]; then
    rm -f sync_cron.log
    echo "   ✅ Logs de synchronisation automatique supprimés"
else
    echo "   ℹ️  Logs conservés"
fi

# 6. Vérification finale
echo "📋 Étape 6: Vérification finale..."
echo "   Processus sync en cours :"
if ps aux | grep -E "(sync.py|run_sync_cron)" | grep -v grep; then
    echo "   ⚠️  Il reste des processus en cours"
else
    echo "   ✅ Aucun processus sync en cours"
fi

echo "   Tâches cron utilisateur :"
if crontab -l 2>/dev/null | grep sync; then
    echo "   ⚠️  Il reste des tâches cron"
else
    echo "   ✅ Aucune tâche cron sync trouvée"
fi

echo ""
echo "🎉 Nettoyage terminé !"
echo ""
echo "💡 Pour relancer la synchronisation automatique plus tard :"
echo "   ./setup_cron.sh"
echo ""
echo "💡 Pour une synchronisation manuelle :"
echo "   ./run_sync.sh"
echo ""
