#!/bin/bash

# Script pour configurer l'exécution automatique de la synchronisation

echo "Configuration de la synchronisation automatique Copper ↔ Mailchimp"
echo "=================================================================="

# Chemin vers le script
SCRIPT_DIR="/home/vboxuser/Desktop/copper_mailchimp_sync/Synchro_Copper_Mailchimp"
SCRIPT_PATH="$SCRIPT_DIR/sync.py"
PYTHON_PATH=$(which python3)

echo "Script path: $SCRIPT_PATH"
echo "Python path: $PYTHON_PATH"

# Créer le script wrapper pour cron
cat > "$SCRIPT_DIR/run_sync_cron.sh" << EOF
#!/bin/bash
cd "$SCRIPT_DIR"
source .env 2>/dev/null || true
$PYTHON_PATH "$SCRIPT_PATH" >> "$SCRIPT_DIR/sync_cron.log" 2>&1
EOF

chmod +x "$SCRIPT_DIR/run_sync_cron.sh"

echo ""
echo "Options de fréquence de synchronisation :"
echo "1. Toutes les 15 minutes (temps réel)"
echo "2. Toutes les heures (fréquent)"
echo "3. Toutes les 4 heures (normal)"
echo "4. Deux fois par jour (8h et 20h)"
echo "5. Une fois par jour (9h du matin)"
echo ""

read -p "Choisissez une option (1-5): " choice

case $choice in
    1)
        CRON_SCHEDULE="*/15 * * * *"
        DESCRIPTION="toutes les 15 minutes"
        ;;
    2)
        CRON_SCHEDULE="0 * * * *"
        DESCRIPTION="toutes les heures"
        ;;
    3)
        CRON_SCHEDULE="0 */4 * * *"
        DESCRIPTION="toutes les 4 heures"
        ;;
    4)
        CRON_SCHEDULE="0 8,20 * * *"
        DESCRIPTION="à 8h et 20h chaque jour"
        ;;
    5)
        CRON_SCHEDULE="0 9 * * *"
        DESCRIPTION="à 9h chaque jour"
        ;;
    *)
        echo "Option invalide"
        exit 1
        ;;
esac

# Ajouter la tâche cron
CRON_ENTRY="$CRON_SCHEDULE $SCRIPT_DIR/run_sync_cron.sh"

echo ""
echo "Ajout de la tâche cron : $DESCRIPTION"
echo "Commande : $CRON_ENTRY"

# Sauvegarder le crontab actuel
crontab -l > /tmp/current_crontab 2>/dev/null || touch /tmp/current_crontab

# Vérifier si la tâche existe déjà
if grep -q "run_sync_cron.sh" /tmp/current_crontab; then
    echo "⚠️  Une tâche de synchronisation existe déjà dans le crontab"
    echo "Contenu actuel :"
    grep "run_sync_cron.sh" /tmp/current_crontab
    echo ""
    read -p "Voulez-vous la remplacer ? (o/n): " replace
    if [[ $replace == "o" || $replace == "O" ]]; then
        # Supprimer l'ancienne entrée
        grep -v "run_sync_cron.sh" /tmp/current_crontab > /tmp/new_crontab
        echo "$CRON_ENTRY" >> /tmp/new_crontab
        crontab /tmp/new_crontab
        echo "✅ Tâche cron mise à jour"
    else
        echo "❌ Opération annulée"
        exit 1
    fi
else
    # Ajouter la nouvelle entrée
    echo "$CRON_ENTRY" >> /tmp/current_crontab
    crontab /tmp/current_crontab
    echo "✅ Tâche cron ajoutée"
fi

# Nettoyer
rm -f /tmp/current_crontab /tmp/new_crontab

echo ""
echo "✅ Configuration terminée !"
echo ""
echo "La synchronisation s'exécutera maintenant $DESCRIPTION"
echo ""
echo "📄 Logs disponibles dans : $SCRIPT_DIR/sync_cron.log"
echo "📄 Logs détaillés dans : $SCRIPT_DIR/sync_log_*.txt"
echo ""
echo "Commandes utiles :"
echo "- Voir le crontab : crontab -l"
echo "- Voir les logs : tail -f $SCRIPT_DIR/sync_cron.log"
echo "- Supprimer la tâche : crontab -e (puis supprimer la ligne)"
echo ""
