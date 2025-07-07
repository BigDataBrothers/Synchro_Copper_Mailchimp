# Copper ↔ Mailchimp Sync

Un outil de synchronisation bidirectionnelle entre Copper CRM et Mailchimp avec gestion des cas particuliers.

## Fonctionnalités

- Synchronisation bidirectionnelle des contacts entre Copper CRM et Mailchimp
- Détection et gestion des emails supprimés définitivement dans Mailchimp
- Génération automatique de liens de réinscription personnalisés
- Ajout d'étiquettes "Réinscription requise" dans Copper
- Génération de rapports détaillés de synchronisation

## Installation

1. Clonez ce dépôt
2. Installez les dépendances :
```bash
pip install python-dotenv requests
```
3. Créez un fichier `.env` dans le répertoire racine avec les variables suivantes :
```
COPPER_API_KEY=votre_clé_api_copper
COPPER_API_EMAIL=votre_email_copper
MAILCHIMP_API_KEY=votre_clé_api_mailchimp
MAILCHIMP_DC=votre_datacenter_mailchimp
MAILCHIMP_LIST_ID=identifiant_de_votre_liste_mailchimp
```

## Utilisation

```bash
python sync.py
```

## Documentation

- Pour les utilisateurs non techniques, consultez [GUIDE_RAPIDE.md](./GUIDE_RAPIDE.md)
- Pour une documentation complète d'utilisation, consultez [DOCUMENTATION.md](./DOCUMENTATION.md)

## Architecture du projet

- `sync.py` : Script principal de synchronisation
- `DOCUMENTATION.md` : Documentation détaillée pour utilisateurs
- `GUIDE_RAPIDE.md` : Guide de référence rapide
- `sync_log_*.txt` : Fichiers de logs générés automatiquement
- `import_report_*.txt` : Rapports d'importation générés automatiquement

## Personnalisation

### Modifier la logique de synchronisation

Pour modifier les règles de synchronisation ou ajouter des champs personnalisés, modifiez les fonctions suivantes dans `sync.py` :
- `sync_copper_to_mailchimp`
- `sync_mailchimp_to_copper`

### Modifier le format des rapports

Pour changer le format des rapports générés, modifiez la fonction `generate_import_report` dans `sync.py`.

## Limitations connues

- Le programme est configuré pour synchroniser uniquement les contacts contenant "@exemple" dans leur email (mode test)
- La synchronisation est limitée aux informations de base des contacts (nom, prénom, email)
- Les limites d'API de Copper et Mailchimp peuvent affecter les performances pour les grandes bases de données

## Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.
