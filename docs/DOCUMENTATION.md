# Documentation : Synchronisation Copper ↔ Mailchimp

## 🚀 Démarrage rapide

**Première installation :**
```bash
./setup_cron.sh  # Choisir option 1 (15 minutes)
```

**Synchronisation manuelle :**
```bash
./run_sync.sh    # Interface en ligne de commande claire
```

**Mode expert :**
```bash
python sync.py   # Exécution directe
```

**Gestion de l'automatisation :**
```bash
crontab -l       # Voir la programmation
crontab -e       # Supprimer la ligne avec "run_sync_cron.sh"
```

## 📚 Documentation spécialisée

Pour des guides détaillés sur des fonctionnalités spécifiques :

- **[GUIDE_RAPIDE.md](./GUIDE_RAPIDE.md)** : Démarrage rapide et utilisation quotidienne
- **[GUIDE_TAG_SUPPRESSION.md](./GUIDE_TAG_SUPPRESSION.md)** : Gestion complète des tags de suppression et workflow d'archivage
- **[TESTS.md](./TESTS.md)** : Documentation détaillée des tests
- **[TESTS_SUMMARY.md](./TESTS_SUMMARY.md)** : Résumé de la batterie de tests
- **[README principal](../README.md)** : Vue d'ensemble technique du projet

## Présentation du programme

Ce programme permet de synchroniser automatiquement les contacts entre Copper (CRM) et Mailchimp (email marketing). Il assure que vos contacts soient à jour dans les deux systèmes et gère les cas spéciaux comme les emails supprimés définitivement dans Mailchimp.

## Fonctionnalités principales

- **Synchronisation bidirectionnelle** : Transfert des contacts de Copper vers Mailchimp et inversement
- **Synchronisation des tags** : Tous les tags Copper sont automatiquement synchronisés vers Mailchimp
- **Gestion intelligente des suppressions** : Détection automatique des contacts marqués avec le tag `🗑️ À SUPPRIMER` (voir [GUIDE_TAG_SUPPRESSION.md](./GUIDE_TAG_SUPPRESSION.md))
- **Exclusion automatique** : Les contacts marqués pour suppression sont automatiquement exclus de la synchronisation
- **Interface de gestion** : Archivage ou suppression sécurisée des contacts marqués
- **Rapports détaillés** : Création de rapports pour suivre chaque opération et son résultat

## Prérequis avant utilisation

1. **Fichier de configuration** : Un fichier `.env` doit être présent dans le même dossier que le programme avec les informations suivantes :

```
COPPER_API_KEY=votre_clé_api_copper
COPPER_API_EMAIL=votre_email_copper
MAILCHIMP_API_KEY=votre_clé_api_mailchimp
MAILCHIMP_DC=votre_datacenter_mailchimp
MAILCHIMP_LIST_ID=identifiant_de_votre_liste_mailchimp
```

2. **Python installé** : Le programme fonctionne avec Python 3.6 ou version supérieure
3. **Bibliothèques requises** : Les bibliothèques Python nécessaires doivent être installées

## Comment utiliser le programme

### Première utilisation

Si c'est la première fois que vous utilisez le programme, suivez ces étapes :

1. Vérifiez que le fichier `.env` est correctement configuré (voir section Prérequis)
2. Ouvrez un terminal (invite de commandes)
3. Naviguez vers le dossier contenant le programme
4. Installez les bibliothèques requises :
   ```
   pip install python-dotenv requests
   ```
5. Exécutez le programme :
   ```
   python sync.py
   ```

### Utilisation régulière

Pour les utilisations suivantes, suivez simplement ces étapes :

1. Ouvrez un terminal (invite de commandes)
2. Naviguez vers le dossier contenant le programme
3. Exécutez le programme :
   ```
   python sync.py
   ```

### Configuration automatique (Recommandé)

Pour configurer la synchronisation automatique périodique :

1. Rendez le script de configuration exécutable :
   ```
   chmod +x setup_cron.sh
   ```
2. Exécutez le script de configuration :
   ```
   ./setup_cron.sh
   ```
3. Choisissez votre fréquence de synchronisation (recommandé : 15 minutes)

Une fois configuré, la synchronisation s'exécutera automatiquement selon l'intervalle choisi.

### Différence entre les scripts de lancement

Le projet contient plusieurs scripts avec des rôles différents :

#### `setup_cron.sh` - Configuration automatique (⚙️ Une seule fois)
- **Rôle** : Configure la synchronisation automatique
- **Utilisation** : Lancez-le une seule fois pour configurer le système
- **Actions** :
  - Vous demande de choisir une fréquence (15 min, 1h, 4h, etc.)
  - Crée automatiquement une tâche dans votre crontab
  - Génère un script optimisé pour l'exécution automatique
- **Commande** : `./setup_cron.sh`

#### `run_sync.sh` - Synchronisation manuelle (🚀 Quand vous voulez)
- **Rôle** : Lance une synchronisation manuelle avec interface en ligne de commande
- **Utilisation** : À chaque fois que vous voulez une synchronisation immédiate
- **Actions** :
  - Affiche une interface claire avec titres et emojis
  - Vérifie les prérequis (.env, Python)
  - Lance la synchronisation et affiche les résultats
  - Guide vers les rapports générés
- **Commande** : `./run_sync.sh`

#### `python sync.py` - Synchronisation directe (⚡ Mode expert)
- **Rôle** : Lance directement le script Python de synchronisation
- **Utilisation** : Pour les utilisateurs avancés ou le debugging
- **Actions** :
  - Exécution directe sans interface
  - Logs détaillés dans les fichiers
- **Commande** : `python sync.py`

**Workflow recommandé :**
1. **Configuration initiale** (une fois) : `./setup_cron.sh`
2. **Synchronisation manuelle** (occasionnelle) : `./run_sync.sh`
3. **Synchronisation automatique** : Le système s'en charge !

## Comprendre les résultats

### 1. Fichiers générés par le programme

Après l'exécution, le programme crée deux types de fichiers :

- **Fichiers de log** : Nom sous forme `sync_log_AAAA-MM-JJ_HH-MM-SS.txt`
  - Contient toutes les étapes et actions réalisées par le programme
  - Utile pour comprendre le déroulement détaillé de la synchronisation

- **Rapports d'importation** : Nom sous forme `import_report_AAAA-MM-JJ_HH-MM-SS.txt`
  - Résumé des opérations de synchronisation
  - Liste des contacts traités avec succès ou en erreur

### 2. Lecture d'un rapport d'importation

Les rapports d'importation sont structurés de la façon suivante :

- **En-tête** : Date et statistiques globales (nombre d'opérations, taux de réussite)
- **Détails des opérations** : Liste des contacts traités avec pour chacun :
  - L'adresse email
  - La direction de synchronisation (Copper → Mailchimp ou Mailchimp → Copper)
  - Le résultat (Succès ou Erreur)
  - Le nom du contact
  - Un lien de réinscription (pour les emails supprimés définitivement)

Exemple de rapport :
```
================================================================================
RAPPORT D'IMPORTATION COPPER ↔ MAILCHIMP
================================================================================
Date: 2025-07-07 14:23:07
Total d'opérations: 2

✅ Succès: 2
❌ Erreurs: 0
📊 Taux de réussite: 100.0%

DÉTAILS DES OPÉRATIONS:
--------------------------------------------------
  1. ✅ SUCCÈS | test3@exemple.fr
     Direction: Mailchimp → Copper
     Nom: Test3 TEST3

  2. ✅ SUCCÈS | test4@exemple.fr
     Direction: Mailchimp → Copper
     Nom: Test4 TEST4
```

### 3. Cas particuliers à surveiller

#### Emails supprimés définitivement

Si un rapport mentionne des "emails supprimés définitivement" ou "forgotten emails", cela signifie que ces contacts :
1. Sont présents dans Copper
2. Ont été supprimés définitivement de Mailchimp (généralement en raison de bounces ou plaintes)

**Action requise** : Pour ces contacts, vous devez :
- Noter le lien de réinscription généré dans le rapport
- Contacter le contact par un autre moyen que l'email
- Lui demander de se réinscrire via ce lien personnalisé

#### Étiquettes "Réinscription requise" dans Copper

Le programme ajoute automatiquement une étiquette "Réinscription requise" aux contacts concernés dans Copper. Vous pouvez filtrer par cette étiquette dans Copper pour identifier facilement ces contacts.

## Fréquence recommandée d'utilisation

### Mode automatique (Recommandé)
Après avoir configuré `setup_cron.sh`, la synchronisation se fait automatiquement :
- **Toutes les 15 minutes** : Synchronisation quasi temps réel (recommandé)
- **Toutes les heures** : Bon compromis entre fréquence et ressources
- **Plusieurs fois par jour** : Pour des besoins moins critiques

### Mode manuel
Si vous n'utilisez pas le mode automatique, exécutez la synchronisation manuellement :
- **Quotidienne** : Pendant les périodes de forte activité (campagnes marketing, événements)
- **Hebdomadaire** : Pour une activité normale
- **À la demande** : Utilisez `./run_sync.sh` quand vous ajoutez de nouveaux contacts

### Choix du script selon la situation
- **Première installation** → `./setup_cron.sh` (configuration automatique)
- **Synchronisation ponctuelle** → `./run_sync.sh` (interface claire)
- **Test ou debugging** → `python sync.py` (logs détaillés)
- **Automatique** → Le cron s'en charge (aucune action requise)

## Résolution des problèmes courants

### Le programme s'arrête avec une erreur de connexion

**Cause possible** : Problème avec les clés API ou la connexion internet

**Solution** :
1. Vérifiez votre connexion internet
2. Assurez-vous que les clés API dans le fichier `.env` sont correctes
3. Vérifiez que vous avez les autorisations nécessaires dans Copper et Mailchimp

### La synchronisation automatique ne fonctionne plus

**Cause possible** : Problème avec le cron ou les permissions

**Solution** :
1. Vérifiez que la tâche cron existe : `crontab -l`
2. Vérifiez les logs cron : `tail -f sync_cron.log`
3. Vérifiez les permissions : `chmod +x run_sync_cron.sh`
4. Si nécessaire, reconfigurez : `./setup_cron.sh`

### Le programme s'exécute mais ne synchronise pas tous les contacts

**Cause possible** : Le programme est configuré pour synchroniser uniquement les contacts contenant "@exemple" dans leur email (mode test)

**Solution** :
- Utilisez le script `toggle_mode.py` pour basculer en mode production :
  ```bash
  python toggle_mode.py
  ```
- Ou modifiez manuellement la variable `TEST_MODE = False` dans le fichier `sync.py`
- ⚠️ ATTENTION: Le mode production traitera TOUTE la base de données

### Je ne trouve pas les contacts synchronisés dans Copper/Mailchimp

**Cause possible** : La synchronisation a échoué ou les contacts sont mal catégorisés

**Solution** :
1. Consultez le rapport d'importation pour vérifier si des erreurs sont mentionnées
2. Dans Copper, essayez de rechercher par email plutôt que par nom
3. Dans Mailchimp, vérifiez que les contacts ne sont pas dans la catégorie "unsubscribed" ou "cleaned"

## Contact support

Si vous rencontrez des difficultés avec ce programme, contactez le service informatique à l'adresse support@votreentreprise.com en précisant :
1. La date et l'heure d'exécution du programme
2. Les fichiers de log et rapport générés
3. Une description précise du problème rencontré

## Gestion de la synchronisation automatique

### Vérifier si la synchronisation automatique est active

Pour voir si une synchronisation automatique est programmée :
```bash
crontab -l
```
Cette commande affiche toutes vos tâches cron. Cherchez une ligne contenant `run_sync_cron.sh`.

### Voir les logs de la synchronisation automatique

Pour suivre l'activité de la synchronisation automatique :
```bash
# Voir les derniers logs cron
tail -f sync_cron.log

# Voir les logs détaillés de la dernière synchronisation
tail -50 sync_log_*.txt | tail -50

# Voir le dernier rapport d'importation
cat $(ls -t import_report_*.txt | head -1)
```

### Modifier la fréquence de synchronisation

Pour changer la fréquence (par exemple passer de 15 minutes à 1 heure) :
```bash
# Relancer la configuration
./setup_cron.sh
# Le script détectera l'ancienne configuration et proposera de la remplacer
```

### Supprimer la synchronisation automatique

Pour arrêter complètement la synchronisation automatique :

**Option 1 : Suppression manuelle (recommandée)**
```bash
# Éditer le crontab
crontab -e
# Supprimer la ligne contenant "run_sync_cron.sh" puis sauvegarder (Ctrl+X, puis Y)
```

**Option 2 : Suppression automatique**
```bash
# Sauvegarder le crontab actuel sans les tâches de sync
crontab -l | grep -v "run_sync_cron.sh" > /tmp/new_crontab
# Appliquer le nouveau crontab
crontab /tmp/new_crontab
# Nettoyer
rm /tmp/new_crontab
```

**Option 3 : Désactiver temporairement**
```bash
# Sauvegarder le crontab actuel
crontab -l > backup_crontab.txt
# Vider le crontab (attention : supprime TOUTES les tâches cron)
crontab -r
# Pour restaurer plus tard :
# crontab backup_crontab.txt
```

### Vérifier que la suppression a fonctionné

Après suppression, vérifiez :
```bash
# Vérifier que la tâche n'existe plus
crontab -l | grep run_sync_cron.sh
# Cette commande ne doit rien afficher

# Optionnel : supprimer les fichiers générés par la configuration
rm -f run_sync_cron.sh sync_cron.log
```

### Nettoyer les anciens logs (optionnel)

Pour libérer de l'espace disque :
```bash
# Supprimer les logs de plus de 30 jours
find . -name "sync_log_*.txt" -mtime +30 -delete
find . -name "import_report_*.txt" -mtime +30 -delete

# Ou supprimer tous les anciens logs (attention : perte des historiques)
rm sync_log_*.txt import_report_*.txt
```

## Optimisation et performance

### Synchronisation intelligente
Le programme intègre plusieurs optimisations pour éviter les synchronisations inutiles :

- **Détection des contacts identiques** : Avant de synchroniser, le programme compare les données (nom, prénom, email) entre Copper et Mailchimp. Si les contacts sont identiques, aucune synchronisation n'est effectuée.

- **Synchronisation différentielle** : Seuls les contacts qui ont réellement changé sont synchronisés, ce qui améliore considérablement les performances.

- **Filtrage en amont** : En mode TEST, seuls les contacts avec "@exemple" sont récupérés et traités, réduisant la charge sur les APIs.

### Messages d'information courants
- `⏭️ Contact identique ignoré: email@exemple.com` : Le contact existe dans les deux systèmes avec des données identiques
- `ℹ️ Aucune synchronisation nécessaire - tous les contacts sont à jour` : Tous les contacts sont déjà synchronisés
- `✅ Synchronisation réussie : X contact(s) traité(s)` : Nombre de contacts réellement synchronisés

Ces optimisations permettent d'exécuter le programme fréquemment (toutes les 15 minutes) sans impact sur les performances.

## Modes de fonctionnement

### Mode TEST (par défaut)
- **Activation** : `TEST_MODE = True` dans le fichier `sync.py`
- **Comportement** : Traite UNIQUEMENT les contacts avec des emails contenant "@exemple"
- **Usage** : Tests, développement, validation des changements
- **Sécurité** : Aucun risque pour la base de données complète

### Mode PRODUCTION
- **Activation** : `TEST_MODE = False` dans le fichier `sync.py`
- **Comportement** : Traite TOUTE la base de données Copper et Mailchimp
- **Usage** : Synchronisation complète en production
- **Sécurité** : ⚠️ ATTENTION - Affecte tous les contacts

### Basculement entre modes
Utilisez le script `toggle_mode.py` pour basculer facilement :
```bash
python toggle_mode.py
```

Le script affiche le mode actuel et demande confirmation avant de basculer.
