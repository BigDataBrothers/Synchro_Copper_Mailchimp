# Copper ↔ Mailchimp Sync

Un outil de synchronisation robuste entre Copper CRM et Mailchimp avec gestion intelligente des suppressions et synchronisation des tags.

## ⚠️ MODES DE FONCTIONNEMENT

### 🧪 Mode TEST (par défaut - SÉCURISÉ)
- **Traite UNIQUEMENT les emails contenant "@exemple"**
- Parfait pour les tests et le développement
- Variable : `TEST_MODE = True` dans `sync.py`
- Aucun risque pour vos données de production

### 🔥 Mode PRODUCTION (sur demande)
- **Traite TOUTE votre base de données Copper et Mailchimp**
- Variable : `TEST_MODE = False` dans `sync.py`
- ⚠️ **ATTENTION** : Impact sur tous vos contacts réels !

### 🔄 Basculement rapide entre modes
```bash
python toggle_mode.py  # Script interactif pour changer de mode
```

## 🚀 Fonctionnalités principales

### Synchronisation
- **Synchronisation bidirectionnelle** des contacts entre Copper CRM et Mailchimp
- **Mode TEST par défaut** : traite uniquement les emails "@exemple" (sécurisé)
- **Mode PRODUCTION** : traite toute la base de données (via `TEST_MODE = False`)
- **Synchronisation des tags** : tous les tags Copper sont synchronisés vers Mailchimp
- **Synchronisation périodique** via cron job (polling)
- **Optimisation intelligente** : ignore les contacts identiques (pas de re-synchronisation inutile)
- **Gestion des erreurs** avec retry automatique

### Gestion des suppressions
- **Détection automatique** des contacts marqués pour suppression (tag `🗑️ À SUPPRIMER`)
- **Exclusion automatique** de la synchronisation pour les contacts marqués
- **Interface en ligne de commande** pour archiver ou supprimer définitivement les contacts
- **Gestion robuste** des variations du tag de suppression (casse, accents, variantes)

### Fonctionnalités avancées
- **Logs détaillés** avec horodatage
- **Rapports d'importation** automatiques (`import_report_*.txt`)
- **Gestion des erreurs Mailchimp** (emails invalides, suppressions, etc.)
- **Comparaison intelligente** : évite les synchronisations inutiles

## 📋 Prérequis

- Python 3.7+
- Accès API Copper CRM
- Accès API Mailchimp
- Permissions d'écriture sur les deux plateformes

## 🔧 Installation

1. **Clonez ce dépôt**
```bash
git clone [URL_DU_REPO]
cd Synchro_Copper_Mailchimp
```

2. **Installez les dépendances**
```bash
pip install -r requirements.txt
```
Ou manuellement :
```bash
pip install python-dotenv requests
```

3. **Configuration des API**

Créez un fichier `.env` dans le répertoire racine :
```env
COPPER_API_KEY=votre_clé_api_copper
COPPER_API_EMAIL=votre_email_copper
MAILCHIMP_API_KEY=votre_clé_api_mailchimp
MAILCHIMP_DC=votre_datacenter_mailchimp
MAILCHIMP_LIST_ID=identifiant_de_votre_liste_mailchimp
SYNC_INTERVAL=3600
```

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

## 📚 Documentation

- **[GUIDE_RAPIDE.md](./GUIDE_RAPIDE.md)** : Guide de référence rapide
- **[GUIDE_TAG_SUPPRESSION.md](./GUIDE_TAG_SUPPRESSION.md)** : Guide détaillé pour la gestion des suppressions
- **[DOCUMENTATION.md](./DOCUMENTATION.md)** : Documentation technique complète

## 🏗️ Architecture

```
Synchro_Copper_Mailchimp/
├── sync.py                     # Script principal
├── run_sync.sh                 # Script d'exécution
├── setup_cron.sh              # Configuration automatique
├── stop_sync.sh               # Arrêt de la synchronisation
├── .env                       # Configuration (à créer)
└── docs/
    ├── README.md
    ├── GUIDE_RAPIDE.md
    ├── GUIDE_TAG_SUPPRESSION.md
    └── DOCUMENTATION.md
```

## ⚙️ Configuration avancée

### Tags de suppression

Le système reconnaît automatiquement ces variantes :
- `🗑️ À SUPPRIMER`
- `🗑️ A SUPPRIMER`
- `À SUPPRIMER`
- `A SUPPRIMER`
- Insensible à la casse et aux espaces

### Synchronisation des tags

Tous les tags Copper sont automatiquement synchronisés vers Mailchimp comme tags personnalisés.

### Logs et monitoring

- Logs rotatifs dans `sync_YYYYMMDD.log`
- Rapports détaillés de chaque synchronisation
- Gestion des erreurs avec retry automatique

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

## Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.
