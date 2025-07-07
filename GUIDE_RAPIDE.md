# Guide Rapide : Synchronisation Copper ↔ Mailchimp

## ⚡️ En bref

Ce programme synchronise vos contacts entre Copper et Mailchimp, et gère les cas où des emails ont été supprimés définitivement de Mailchimp.

## 🚀 Lancement du programme

1. Ouvrez un terminal
2. Naviguez vers le dossier du programme : `cd chemin/vers/dossier`
3. Exécutez la commande : `python sync.py`
4. Attendez la fin de l'exécution

## 📊 Où trouver les résultats

Après exécution, deux fichiers sont créés dans le dossier du programme :

- **Rapport d'importation** : `import_report_DATE_HEURE.txt`
- **Log détaillé** : `sync_log_DATE_HEURE.txt`

## 🔍 Comment lire les rapports

### Succès (✅)
```
✅ SUCCÈS | exemple@email.com
Direction: Mailchimp → Copper
Nom: Jean Dupont
```
➡️ Ce contact a été correctement synchronisé, aucune action requise.

### Email supprimé (⚠️)
```
⚠️ EMAIL SUPPRIMÉ | exemple@email.com
Direction: Copper → Mailchimp
Nom: Marie Martin
Lien de réinscription: https://...
```
➡️ Action requise : Contacter cette personne par un autre moyen et lui demander de se réinscrire via le lien fourni.

### Erreur (❌)
```
❌ ERREUR | exemple@email.com
Direction: Copper → Mailchimp
Nom: Paul Durand
Raison: Invalid email format
```
➡️ Action requise : Vérifier et corriger l'adresse email dans Copper.

## 🏷️ Étiquettes dans Copper

- **"Réinscription requise"** : Cette étiquette est automatiquement ajoutée aux contacts dont l'email a été supprimé définitivement dans Mailchimp.

## 📱 Besoin d'aide?

Contactez le support à support@votreentreprise.com en incluant :
1. Date et heure d'exécution
2. Fichiers de rapport générés
3. Description du problème

---
Pour une documentation complète, consultez le fichier DOCUMENTATION.md
