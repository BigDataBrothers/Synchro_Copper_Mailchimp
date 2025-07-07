# Documentation : Synchronisation Copper ↔ Mailchimp

## Présentation du programme

Ce programme permet de synchroniser automatiquement les contacts entre Copper (CRM) et Mailchimp (email marketing). Il assure que vos contacts soient à jour dans les deux systèmes et gère les cas spéciaux comme les emails supprimés définitivement dans Mailchimp.

## Fonctionnalités principales

- **Synchronisation bidirectionnelle** : Transfert des contacts de Copper vers Mailchimp et inversement
- **Gestion des emails supprimés** : Détection des emails supprimés définitivement dans Mailchimp avec création de liens de réinscription
- **Étiquetage automatique** : Ajout d'étiquettes "Réinscription requise" dans Copper pour les contacts concernés
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

Pour maintenir vos bases de données synchronisées, nous recommandons d'exécuter ce programme :
- **Hebdomadaire** : Pour une activité normale
- **Quotidienne** : Pendant les périodes de forte activité (campagnes marketing, événements)

## Résolution des problèmes courants

### Le programme s'arrête avec une erreur de connexion

**Cause possible** : Problème avec les clés API ou la connexion internet

**Solution** :
1. Vérifiez votre connexion internet
2. Assurez-vous que les clés API dans le fichier `.env` sont correctes
3. Vérifiez que vous avez les autorisations nécessaires dans Copper et Mailchimp

### Le programme s'exécute mais ne synchronise pas tous les contacts

**Cause possible** : Le programme est configuré pour synchroniser uniquement les contacts contenant "@exemple" dans leur email (mode test)

**Solution** :
- Si vous souhaitez synchroniser tous les contacts, contactez l'équipe technique pour modifier cette limitation

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
