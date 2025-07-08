#!/usr/bin/env python3
"""
Version finale du script avec synchronisation des tags vers Mailchimp
"""

import os
import requests
import hashlib
import traceback
from dotenv import load_dotenv
from datetime import datetime
import json
import time

load_dotenv()

# Configuration du logging
log_filename = f"sync_log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
log_file = open(log_filename, "w", encoding='utf-8')

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'

def log(message, level="INFO"):
    timestamp = datetime.now().strftime('%H:%M:%S')
    color = {"INFO": Colors.BLUE, "SUCCESS": Colors.GREEN, "WARNING": Colors.YELLOW, "ERROR": Colors.RED}.get(level, "")
    icon = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌"}.get(level, "📝")
    
    console_message = f"{color}[{timestamp}] {icon} {message}{Colors.END}"
    file_message = f"[{timestamp}] {icon} {message}"
    
    print(console_message)
    log_file.write(file_message + "\n")
    log_file.flush()

# Configuration APIs
COPPER_API_URL = os.getenv("COPPER_API_URL", "https://api.copper.com/developer_api/v1")
COPPER_API_EMAIL = os.getenv("COPPER_API_EMAIL")
COPPER_API_KEY = os.getenv("COPPER_API_KEY")

MC_API_KEY = os.getenv("MAILCHIMP_API_KEY")
MC_DC = os.getenv("MAILCHIMP_DC")
MC_LIST_ID = os.getenv("MAILCHIMP_LIST_ID")
MC_BASE = f"https://{MC_DC}.api.mailchimp.com/3.0"
MC_AUTH = ("anystring", MC_API_KEY)

COPPER_HEADERS = {
    "X-PW-AccessToken": COPPER_API_KEY,
    "X-PW-Application": "developer_api",
    "X-PW-UserEmail": COPPER_API_EMAIL,
    "Content-Type": "application/json"
}

def is_delete_tag_robust(tag):
    """Détection robuste du tag de suppression"""
    if not tag or not isinstance(tag, str):
        return False
    
    normalized = str(tag).strip().upper()
    normalized = normalized.replace('À', 'A').replace('Á', 'A').replace('Â', 'A')
    normalized = normalized.replace('È', 'E').replace('É', 'É').replace('Ê', 'E')
    
    conditions = [
        "SUPPRIMER" in normalized,
        "🗑" in normalized,
        "DELETE" in normalized,
        "REMOVE" in normalized,
        "A SUPPRIMER" in normalized
    ]
    
    return any(conditions)

def normalize_email(email):
    """Normalise un email"""
    return email.lower().strip()

def is_target_email(email):
    """Vérifie si l'email est dans le scope de test"""
    return "@exemple" in email.lower()

def get_subscriber_hash(email):
    """Génère le hash subscriber pour Mailchimp"""
    return hashlib.md5(email.lower().encode()).hexdigest()

def safe_request(func, *args, **kwargs):
    """Wrapper pour les requêtes avec retry"""
    max_retries = 2
    retry_delay = 0.5
    
    for attempt in range(max_retries):
        try:
            response = func(*args, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                log(f"Échec définitif après {max_retries} tentatives: {e}", "ERROR")
                raise
            log(f"Tentative {attempt + 1} échouée: {e}. Retry dans {retry_delay}s", "WARNING")
            time.sleep(retry_delay)

def get_all_copper_contacts():
    """Récupère tous les contacts Copper"""
    log("🔄 Récupération de TOUS les contacts Copper...", "INFO")
    contacts = []
    page = 1
    
    while True:
        url = f"{COPPER_API_URL}/people/search"
        payload = {"page_number": page, "page_size": 200}
        
        response = safe_request(requests.post, url, headers=COPPER_HEADERS, json=payload)
        data = response.json()
        
        if not data:
            break
            
        contacts.extend(data)
        log(f"   Page {page}: +{len(data)} contacts (Total: {len(contacts)})", "INFO")
        
        if len(data) < 200:
            break
            
        page += 1
    
    log(f"✅ {len(contacts)} contacts Copper récupérés", "SUCCESS")
    return contacts

def sync_contact_to_mailchimp(contact, tags_to_sync=None):
    """Synchronise un contact vers Mailchimp avec ses tags"""
    emails = contact.get("emails", [])
    if not emails:
        return False
    
    email = emails[0]["email"]
    
    # Ne synchroniser que les emails de test
    if not is_target_email(email):
        return False
    
    first_name = contact.get("first_name", "")
    last_name = contact.get("last_name", "")
    
    # Préparer les tags pour Mailchimp
    mailchimp_tags = []
    if tags_to_sync:
        for tag in tags_to_sync:
            # Nettoyer les tags pour Mailchimp (max 50 caractères)
            clean_tag = str(tag)[:50]
            mailchimp_tags.append({"name": clean_tag, "status": "active"})
    
    # Données pour Mailchimp
    mailchimp_data = {
        "email_address": email,
        "status_if_new": "subscribed",
        "merge_fields": {
            "FNAME": first_name,
            "LNAME": last_name
        }
    }
    
    try:
        subscriber_hash = get_subscriber_hash(email)
        url = f"{MC_BASE}/lists/{MC_LIST_ID}/members/{subscriber_hash}"
        
        # Synchroniser le contact
        response = safe_request(requests.put, url, auth=MC_AUTH, json=mailchimp_data)
        
        # Synchroniser les tags si fournis
        if mailchimp_tags:
            tags_url = f"{MC_BASE}/lists/{MC_LIST_ID}/members/{subscriber_hash}/tags"
            tags_payload = {"tags": mailchimp_tags}
            
            tag_response = safe_request(requests.post, tags_url, auth=MC_AUTH, json=tags_payload)
            log(f"✅ Synchronisé avec tags: {email} ({len(mailchimp_tags)} tags)", "SUCCESS")
        else:
            log(f"✅ Synchronisé: {email}", "SUCCESS")
        
        return True
        
    except Exception as e:
        log(f"❌ Erreur sync {email}: {e}", "ERROR")
        return False

def handle_marked_contacts(marked_contacts):
    """Gère les contacts marqués pour suppression"""
    if not marked_contacts:
        log("✅ Aucun contact marqué pour suppression", "SUCCESS")
        return
    
    log(f"⚠️ {len(marked_contacts)} contact(s) marqué(s) pour suppression détecté(s)", "WARNING")
    
    # Affichage des contacts
    for i, contact in enumerate(marked_contacts, 1):
        log(f"   {i}. {contact['email']} - {contact['name']} (Tag: '{contact['detected_tag']}')", "INFO")
    
    choice = input("\n🤔 Que voulez-vous faire ? (t=traiter un par un, g=traiter en groupe, i=ignorer): ").lower()
    
    if choice == "i":
        log("ℹ️ Contacts ignorés pour cette session", "INFO")
    elif choice == "g":
        action = input("Action pour tous (a=archiver, s=supprimer): ").lower()
        if action == "a":
            log("🔄 Archivage en cours...", "INFO")
            for contact in marked_contacts:
                archive_contact(contact)
        elif action == "s":
            log("🔄 Suppression en cours...", "INFO")
            for contact in marked_contacts:
                delete_contact(contact)
    elif choice == "t":
        for contact in marked_contacts:
            print(f"\n📧 Contact: {contact['email']} - {contact['name']}")
            action = input("Action (a=archiver, s=supprimer, i=ignorer): ").lower()
            if action == "a":
                archive_contact(contact)
            elif action == "s":
                delete_contact(contact)

def archive_contact(contact):
    """Archive un contact (désabonnement Mailchimp)"""
    try:
        email = contact["email"]
        subscriber_hash = get_subscriber_hash(email)
        url = f"{MC_BASE}/lists/{MC_LIST_ID}/members/{subscriber_hash}"
        
        response = safe_request(requests.patch, url, auth=MC_AUTH, 
                              json={"status": "unsubscribed"})
        
        log(f"✅ Contact {email} archivé (désabonné)", "SUCCESS")
    except Exception as e:
        log(f"❌ Erreur archivage {contact['email']}: {e}", "ERROR")

def delete_contact(contact):
    """Supprime un contact (Copper + Mailchimp)"""
    try:
        email = contact["email"]
        
        # Supprimer de Mailchimp
        subscriber_hash = get_subscriber_hash(email)
        url = f"{MC_BASE}/lists/{MC_LIST_ID}/members/{subscriber_hash}"
        response = safe_request(requests.delete, url, auth=MC_AUTH)
        
        # Supprimer de Copper
        copper_url = f"{COPPER_API_URL}/people/{contact['copper_id']}"
        response = safe_request(requests.delete, copper_url, headers=COPPER_HEADERS)
        
        log(f"✅ Contact {email} supprimé (Copper + Mailchimp)", "SUCCESS")
    except Exception as e:
        log(f"❌ Erreur suppression {contact['email']}: {e}", "ERROR")

def main():
    """Fonction principale avec synchronisation des tags"""
    start_time = time.time()
    
    log("🚀 SYNCHRONISATION COPPER-MAILCHIMP AVEC TAGS", "INFO")
    log("=" * 60, "INFO")
    
    try:
        # 1. Récupération des contacts
        copper_contacts = get_all_copper_contacts()
        
        # 2. Analyse et traitement
        marked_contacts = []
        synced_contacts = 0
        excluded_contacts = 0
        
        log("🔄 Analyse et synchronisation des contacts...", "INFO")
        
        for contact in copper_contacts:
            tags = contact.get("tags", [])
            
            # Vérifier si marqué pour suppression
            is_marked = False
            detected_tag = None
            
            for tag_name in tags:
                if is_delete_tag_robust(str(tag_name)):
                    is_marked = True
                    detected_tag = tag_name
                    break
            
            if is_marked:
                # Contact marqué pour suppression
                emails = contact.get("emails", [])
                if emails:
                    marked_contacts.append({
                        "email": emails[0]["email"],
                        "name": f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip(),
                        "copper_id": contact.get("id"),
                        "detected_tag": detected_tag
                    })
                excluded_contacts += 1
            else:
                # Contact normal - synchroniser avec tags
                if sync_contact_to_mailchimp(contact, tags):
                    synced_contacts += 1
        
        # 3. Résultats
        log(f"📊 Résultats:", "INFO")
        log(f"   Contacts synchronisés: {synced_contacts}", "INFO")
        log(f"   Contacts exclus: {excluded_contacts}", "INFO")
        log(f"   Contacts marqués pour suppression: {len(marked_contacts)}", "INFO")
        
        # 4. Gestion des contacts marqués
        handle_marked_contacts(marked_contacts)
        
        execution_time = time.time() - start_time
        log(f"✅ SYNCHRONISATION TERMINÉE en {execution_time:.2f}s", "SUCCESS")
        
    except Exception as e:
        log(f"❌ ERREUR CRITIQUE: {e}", "ERROR")
        log(f"🔍 Traceback: {traceback.format_exc()}", "ERROR")
    
    finally:
        log_file.close()

if __name__ == "__main__":
    main()
