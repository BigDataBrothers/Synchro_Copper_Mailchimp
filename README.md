# 🔄 Copper ↔ Mailchimp Sync

[![Tests](https://img.shields.io/badge/tests-99%20passed-brightgreen)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-72%25-green)](test_reports/)
[![Python](https://img.shields.io/badge/python-3.7%2B-blue)](requirements.txt)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

Un outil de synchronisation robuste et sécurisé entre Copper CRM et Mailchimp avec gestion intelligente des suppressions et tests automatisés.

## 🚀 Démarrage Rapide

### 1. Installation
```bash
git clone [ce-repo]
cd Sync_Copper_Mailchimp
pip install -r requirements.txt
```

### 2. Configuration
```bash
# Copiez le template de configuration
cp .env.example .env

# Éditez .env avec vos vraies clés API
nano .env
```

### 3. Premier test (sécurisé)
```bash
# Le mode TEST est activé par défaut (emails @exemple uniquement)
python sync.py
```

### 4. Configuration automatique
```bash
# Configurez la synchronisation automatique
./setup_cron.sh
```

## 📚 Documentation

- **[Guide Rapide](docs/GUIDE_RAPIDE.md)** - Démarrage et utilisation quotidienne
- **[Documentation Complète](docs/DOCUMENTATION.md)** - Guide technique détaillé
- **[Guide Tags](docs/GUIDE_TAG_SUPPRESSION.md)** - Gestion des suppressions
- **[Tests](docs/TESTS.md)** - Documentation des tests
- **[Résumé Tests](docs/TESTS_SUMMARY.md)** - Résumé de la batterie de tests

## ✨ Fonctionnalités

### Synchronisation
- 🔄 **Synchronisation bidirectionnelle** Copper ↔ Mailchimp
- 🏷️ **Synchronisation des tags** automatique
- 🛡️ **Mode TEST** sécurisé par défaut (emails @exemple uniquement)
- � **Mode PRODUCTION** pour toute la base de données
- ⚡ **Optimisations** (ignore les doublons, pas de re-synchronisation inutile)
- 🔄 **Synchronisation périodique** via cron job (polling)
- 🔄 **Gestion des erreurs** avec retry automatique

### Gestion des suppressions
- �️ **Détection automatique** des contacts marqués pour suppression
- 🚫 **Exclusion automatique** de la synchronisation
- 🗂️ **Interface en ligne de commande** pour archiver ou supprimer
- 🔤 **Gestion robuste** des variations du tag (casse, accents, variantes)

### Fonctionnalités avancées
- 📊 **Logs détaillés** avec horodatage
- 📋 **Rapports d'importation** automatiques
- � **Gestion des erreurs Mailchimp** (emails invalides, suppressions)
- 🔍 **Comparaison intelligente** pour éviter les synchronisations inutiles

## 🧪 Tests

```bash
# Tous les tests (99 tests)
./run_tests.sh

# Tests avec couverture
make test-coverage

# Tests rapides
make test-unit
```

**99 tests** - 72% de couverture - Tests d'intégration inclus

## ⚙️ Configuration

### Variables d'environnement (.env)
```env
COPPER_API_KEY=votre_clé_api_copper
COPPER_API_EMAIL=votre_email_copper
MAILCHIMP_API_KEY=votre_clé_api_mailchimp
MAILCHIMP_DC=votre_datacenter_mailchimp
MAILCHIMP_LIST_ID=identifiant_de_votre_liste_mailchimp
SYNC_INTERVAL=3600
```

### Modes de fonctionnement
- **🧪 TEST** (défaut) : Emails `@exemple` uniquement - **SÉCURISÉ**
- **🔥 PRODUCTION** : Toute la base de données - **ATTENTION**

### Basculement de mode
```bash
python toggle_mode.py  # Interface interactive
```

### Tags de suppression reconnus
- `🗑️ À SUPPRIMER` / `🗑️ A SUPPRIMER`
- `À SUPPRIMER` / `A SUPPRIMER`
- `DELETE` / `REMOVE` / `INACTIVE` / `ARCHIVED`
- Insensible à la casse et aux espaces

## 🔧 Scripts Disponibles

- `./run_sync.sh` - Synchronisation manuelle
- `./setup_cron.sh` - Configuration automatique
- `./run_tests.sh` - Exécution des tests
- `./stop_sync.sh` - Arrêt de la synchronisation

## 📋 Prérequis

- Python 3.7+
- Clés API Copper CRM
- Clés API Mailchimp
- Permissions d'écriture sur les deux plateformes

## 🏗️ Architecture

```
Sync_Copper_Mailchimp/
├── sync.py                     # Script principal
├── toggle_mode.py              # Basculement TEST/PRODUCTION
├── run_sync.sh                 # Script d'exécution
├── run_tests.sh                # Script de tests
├── setup_cron.sh               # Configuration automatique
├── stop_sync.sh                # Arrêt de la synchronisation
├── .env                        # Configuration (à créer)
├── .env.example                # Template de configuration
├── requirements.txt            # Dépendances Python
├── Makefile                    # Commandes automatisées
├── pytest.ini                 # Configuration des tests
├── tests/                      # Suite de tests (99 tests)
│   ├── test_utils.py           # Tests utilitaires
│   ├── test_api.py             # Tests API
│   ├── test_reporting.py       # Tests rapports
│   ├── test_performance.py     # Tests performance
│   └── test_integration.py     # Tests intégration
└── docs/                       # Documentation
    ├── GUIDE_RAPIDE.md
    ├── DOCUMENTATION.md
    ├── GUIDE_TAG_SUPPRESSION.md
    ├── TESTS.md
    └── TESTS_SUMMARY.md        # Résumé des tests
```

## 🔄 Workflow de synchronisation

1. **Lecture des contacts** Copper et Mailchimp
2. **Détection des contacts marqués** pour suppression
3. **Exclusion automatique** des contacts marqués
4. **Synchronisation bidirectionnelle** des contacts valides
5. **Synchronisation des tags** Copper → Mailchimp
6. **Interface utilisateur** pour traiter les suppressions
7. **Génération des rapports**

## ⚠️ Limitations

- **Respect des limites API** Copper et Mailchimp
- **Gestion des gros volumes** avec pagination automatique
- **Tags Mailchimp** limités aux caractères alphanumériques

## 🐛 Dépannage

### Problèmes fréquents

1. **Erreur d'authentification** : Vérifiez vos clés API dans `.env`
2. **Contact non synchronisé** : Vérifiez s'il n'a pas le tag de suppression
3. **Tag non créé** : Mailchimp convertit automatiquement les caractères spéciaux

### Logs

Consultez les fichiers de logs pour diagnostiquer :
```bash
tail -f sync_$(date +%Y%m%d).log
```

## 🛡️ Sécurité

- ✅ **Mode TEST par défaut** (emails @exemple uniquement)
- ✅ **Variables d'environnement** pour les clés API
- ✅ **Fichier .env ignoré** par git
- ✅ **Validation des données** d'entrée
- ✅ **Gestion d'erreurs robuste** avec retry
- ✅ **Pas d'appels API réels** dans les tests
- ✅ **Isolation des environnements** TEST/PRODUCTION

## 🚀 Utilisation

### Synchronisation manuelle
```bash
python sync.py
```

### Configuration de la synchronisation automatique
```bash
# Rendre les scripts exécutables
chmod +x setup_cron.sh run_sync.sh

# Configurer le cron job
./setup_cron.sh
```

### Gestion des contacts marqués pour suppression

Le système détecte automatiquement les contacts avec le tag `🗑️ À SUPPRIMER` et propose :
- **Archiver** : déplacer vers les archives Copper
- **Supprimer** : suppression définitive
- **Ignorer** : conserver mais exclure de la synchronisation

## 📄 Licence

MIT License - Voir [LICENSE](LICENSE)

---

**🎯 Prêt pour la production** - Tests validés - Documentation complète
