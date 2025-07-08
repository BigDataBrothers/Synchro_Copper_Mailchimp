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

def is_inactive_tag(tag):
    """Détection du tag inactif"""
    if not tag or not isinstance(tag, str):
        return False
    
    normalized = str(tag).strip().upper()
    normalized = normalized.replace('À', 'A').replace('Á', 'A').replace('Â', 'A')
    normalized = normalized.replace('È', 'E').replace('É', 'É').replace('Ê', 'E')
    
    conditions = [
        "INACTIF" in normalized,
        "📥" in normalized,
        "INACTIVE" in normalized,
        "ARCHIVED" in normalized
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

def get_target_copper_contacts():
    """Récupère seulement les contacts Copper avec emails @exemple (optimisé)"""
    log("🔄 Récupération des contacts Copper cibles (@exemple)...", "INFO")
    contacts = []
    page = 1
    
    while True:
        url = f"{COPPER_API_URL}/people/search"
        payload = {"page_number": page, "page_size": 200}
        
        response = safe_request(requests.post, url, headers=COPPER_HEADERS, json=payload)
        data = response.json()
        
        if not data:
            break
        
        # Filtrer immédiatement les contacts avec @exemple
        target_contacts = []
        for contact in data:
            emails = contact.get("emails", [])
            if emails and is_target_email(emails[0]["email"]):
                target_contacts.append(contact)
        
        contacts.extend(target_contacts)
        log(f"   Page {page}: +{len(target_contacts)} contacts cibles (Total: {len(contacts)})", "INFO")
        
        if len(data) < 200:
            break
            
        page += 1
    
    log(f"✅ {len(contacts)} contacts Copper cibles récupérés", "SUCCESS")
    return contacts

def sync_contact_to_mailchimp(contact, tags_to_sync=None):
    """Synchronise un contact vers Mailchimp avec ses tags (optimisé)"""
    emails = contact.get("emails", [])
    if not emails:
        return False
    
    email = emails[0]["email"]
    
    # Emails déjà filtrés en amont, pas besoin de re-vérifier
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
    """Archive un contact (statut Inactif dans Copper + désabonnement Mailchimp)"""
    try:
        email = contact["email"]
        copper_id = contact["copper_id"]
        
        # 1. Marquer comme inactif dans Copper (ajout d'un tag)
        copper_url = f"{COPPER_API_URL}/people/{copper_id}"
        
        # Récupérer le contact actuel pour conserver ses tags existants
        response = safe_request(requests.get, copper_url, headers=COPPER_HEADERS)
        current_contact = response.json()
        
        # Ajouter le tag "📥 INACTIF" aux tags existants
        existing_tags = current_contact.get("tags", [])
        if "📥 INACTIF" not in existing_tags:
            existing_tags.append("📥 INACTIF")
        
        # Supprimer le tag de suppression et ajouter le tag inactif
        existing_tags = [tag for tag in existing_tags if not is_delete_tag_robust(str(tag))]
        existing_tags.append("📥 INACTIF")
        
        # Mettre à jour le contact dans Copper
        update_payload = {"tags": existing_tags}
        response = safe_request(requests.put, copper_url, headers=COPPER_HEADERS, json=update_payload)
        
        # 2. Désabonner de Mailchimp
        subscriber_hash = get_subscriber_hash(email)
        mc_url = f"{MC_BASE}/lists/{MC_LIST_ID}/members/{subscriber_hash}"
        
        response = safe_request(requests.patch, mc_url, auth=MC_AUTH, 
                              json={"status": "unsubscribed"})
        
        log(f"✅ Contact {email} archivé (Inactif dans Copper + désabonné Mailchimp)", "SUCCESS")
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

def get_target_mailchimp_contacts():
    """Récupère seulement les contacts Mailchimp avec emails @exemple (optimisé)"""
    log("🔄 Récupération des contacts Mailchimp cibles (@exemple)...", "INFO")
    members = []
    offset = 0
    count = 1000
    
    while True:
        url = f"{MC_BASE}/lists/{MC_LIST_ID}/members"
        params = {
            "offset": offset,
            "count": count,
            "status": "subscribed"
        }
        
        response = safe_request(requests.get, url, auth=MC_AUTH, params=params)
        data = response.json()
        
        batch = data.get("members", [])
        if not batch:
            break
        
        # Filtrer immédiatement les contacts avec @exemple
        target_members = []
        for member in batch:
            email = member.get("email_address", "")
            if is_target_email(email):
                target_members.append(member)
        
        members.extend(target_members)
        log(f"   Offset {offset}: +{len(target_members)} membres cibles (Total: {len(members)})", "INFO")
        
        if len(batch) < count:
            break
            
        offset += count
    
    log(f"✅ {len(members)} membres Mailchimp cibles récupérés", "SUCCESS")
    return members

def sync_mailchimp_to_copper(mc_members, copper_contacts_by_email):
    """Synchronise Mailchimp vers Copper (optimisé)"""
    synced_count = 0
    
    for member in mc_members:
        email = normalize_email(member.get("email_address", ""))
        
        # Vérifier si le contact existe déjà dans Copper
        if email in copper_contacts_by_email:
            continue  # Contact déjà présent
            
        # Créer le contact dans Copper
        first_name = member.get("merge_fields", {}).get("FNAME", "")
        last_name = member.get("merge_fields", {}).get("LNAME", "")
        
        if not first_name and not last_name:
            continue  # Skip si pas de nom
            
        contact_data = {
            "name": f"{first_name} {last_name}".strip(),
            "emails": [{"email": email, "category": "work"}],
            "first_name": first_name,
            "last_name": last_name
        }
        
        try:
            url = f"{COPPER_API_URL}/people"
            response = safe_request(requests.post, url, headers=COPPER_HEADERS, json=contact_data)
            
            log(f"✅ Nouveau contact créé dans Copper: {email}", "SUCCESS")
            synced_count += 1
            
        except Exception as e:
            log(f"❌ Erreur création {email} dans Copper: {e}", "ERROR")
    
    return synced_count

def main():
    """Fonction principale avec synchronisation des tags"""
    start_time = time.time()
    
    log("🚀 SYNCHRONISATION BIDIRECTIONNELLE COPPER ↔ MAILCHIMP", "INFO")
    log("=" * 60, "INFO")
    
    try:
        # 1. Récupération optimisée des contacts cibles uniquement
        log("🎯 RÉCUPÉRATION OPTIMISÉE (emails @exemple uniquement)", "INFO")
        copper_contacts = get_target_copper_contacts()
        mailchimp_members = get_target_mailchimp_contacts()
        
        # 2. Construction des index optimisés
        log("🔧 Construction des index email...", "INFO")
        copper_by_email = {}
        mc_by_email = {}
        
        for contact in copper_contacts:
            emails = contact.get("emails", [])
            if emails:
                email = normalize_email(emails[0]["email"])
                copper_by_email[email] = contact
        
        for member in mailchimp_members:
            email = normalize_email(member.get("email_address", ""))
            mc_by_email[email] = member
        
        log(f"✅ Index créés: {len(copper_by_email)} contacts Copper cibles, {len(mc_by_email)} membres Mailchimp cibles", "SUCCESS")
        
        # Vérification s'il y a des contacts à traiter
        if len(copper_by_email) == 0 and len(mc_by_email) == 0:
            log(f"ℹ️ Aucun contact cible trouvé (@exemple) - rien à synchroniser", "INFO")
            execution_time = time.time() - start_time
            log(f"✅ SYNCHRONISATION TERMINÉE en {execution_time:.2f}s (aucun contact à traiter)", "SUCCESS")
            return
        
        # 3. Analyse et traitement des contacts Copper
        marked_contacts = []
        copper_to_mc_synced = 0
        excluded_contacts = 0
        
        log("🔄 Analyse et synchronisation Copper → Mailchimp...", "INFO")
        
        for contact in copper_contacts:
            tags = contact.get("tags", [])
            
            # Vérifier si marqué pour suppression
            is_marked = False
            is_inactive = False
            detected_tag = None
            
            for tag_name in tags:
                if is_delete_tag_robust(str(tag_name)):
                    is_marked = True
                    detected_tag = tag_name
                    break
                elif is_inactive_tag(str(tag_name)):
                    is_inactive = True
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
            elif is_inactive:
                # Contact inactif - exclure de la synchronisation
                excluded_contacts += 1
            else:
                # Contact normal - synchroniser avec tags
                if sync_contact_to_mailchimp(contact, tags):
                    copper_to_mc_synced += 1
        
        # 4. Synchronisation Mailchimp → Copper (optimisée)
        log("🔄 Synchronisation Mailchimp → Copper...", "INFO")
        mc_to_copper_synced = sync_mailchimp_to_copper(mailchimp_members, copper_by_email)
        
        # 5. Résultats détaillés
        total_synced = copper_to_mc_synced + mc_to_copper_synced
        log(f"📊 Résultats de la synchronisation bidirectionnelle:", "INFO")
        log(f"   Contacts Copper → Mailchimp: {copper_to_mc_synced}", "INFO")
        log(f"   Contacts Mailchimp → Copper: {mc_to_copper_synced}", "INFO")
        log(f"   Total synchronisé: {total_synced}", "INFO")
        log(f"   Contacts exclus (inactifs): {excluded_contacts}", "INFO")
        log(f"   Contacts marqués pour suppression: {len(marked_contacts)}", "INFO")
        
        if total_synced > 0:
            log(f"✅ Synchronisation réussie : {total_synced} contact(s) traité(s)", "SUCCESS")
        else:
            log(f"ℹ️ Aucune synchronisation nécessaire - tous les contacts sont à jour", "INFO")
        
        # 6. Gestion des contacts marqués
        handle_marked_contacts(marked_contacts)
        
        execution_time = time.time() - start_time
        log(f"✅ SYNCHRONISATION BIDIRECTIONNELLE TERMINÉE en {execution_time:.2f}s", "SUCCESS")
        
    except Exception as e:
        log(f"❌ ERREUR CRITIQUE: {e}", "ERROR")
        log(f"🔍 Traceback: {traceback.format_exc()}", "ERROR")
    
    finally:
        log_file.close()

if __name__ == "__main__":
    main()
