import os
import requests
import hashlib
from dotenv import load_dotenv
from datetime import datetime
import json
import time
from typing import Optional, Dict, List

# === Charger les variables d'environnement
load_dotenv()

# === Configuration du logging
log_filename = f"sync_log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
log_file = open(log_filename, "w", encoding='utf-8')

def log(message):
    timestamp = datetime.now().strftime('%H:%M:%S')
    formatted_message = f"[{timestamp}] {message}"
    print(formatted_message)
    log_file.write(formatted_message + "\n")
    log_file.flush()

# === Configuration Copper
COPPER_API_KEY = os.getenv("COPPER_API_KEY")
COPPER_API_EMAIL = os.getenv("COPPER_API_EMAIL")
COPPER_API_URL = os.getenv("COPPER_API_URL", "https://api.copper.com/developer_api/v1")
COPPER_HEADERS = {
    "X-PW-AccessToken": COPPER_API_KEY,
    "X-PW-Application": "developer_api",
    "X-PW-UserEmail": COPPER_API_EMAIL,
    "Content-Type": "application/json"
}

# === Configuration Mailchimp
MC_API_KEY = os.getenv("MAILCHIMP_API_KEY")
MC_DC = os.getenv("MAILCHIMP_DC")
MC_LIST_ID = os.getenv("MAILCHIMP_LIST_ID")
MC_BASE = f"https://{MC_DC}.api.mailchimp.com/3.0"
MC_AUTH = ("anystring", MC_API_KEY)

# === Utilitaires
def get_subscriber_hash(email: str) -> str:
    """Génère le hash MD5 pour l'email Mailchimp"""
    return hashlib.md5(email.encode('utf-8')).hexdigest()

def is_target_email(email: str) -> bool:
    """Vérifie si l'email contient @exemple (pour les tests)"""
    return "@exemple" in email.lower()

def normalize_email(email: str) -> str:
    """Normalise l'email (lowercase, strip)"""
    return email.strip().lower() if email else ""

def safe_request(func, *args, **kwargs):
    """Wrapper pour les requêtes avec gestion d'erreurs et retry"""
    max_retries = 3
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            response = func(*args, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                log(f"⚠️  Tentative {attempt + 1} échouée, retry dans {retry_delay}s: {e}")
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                log(f"❌ Erreur de requête après {max_retries} tentatives: {e}")
                if hasattr(e, 'response') and e.response is not None:
                    try:
                        error_data = e.response.json()
                        log(f"   Détails erreur: {error_data}")
                    except:
                        log(f"   Status: {e.response.status_code}, Réponse: {e.response.text[:200]}")
                return None
    
    return None

# === Fonctions API Copper
def get_copper_people() -> List[Dict]:
    """Récupère toutes les personnes de Copper avec pagination"""
    url = f"{COPPER_API_URL}/people/search"
    all_people = []
    page = 1
    
    log("🔄 Récupération des contacts Copper...")
    
    while True:
        payload = {
            "page_number": page,
            "page_size": 200
        }
        
        response = safe_request(requests.post, url, headers=COPPER_HEADERS, json=payload)
        if not response:
            log(f"❌ Erreur lors de la récupération page {page}")
            break
            
        try:
            data = response.json()
            people = data if isinstance(data, list) else []
            
            if not people:
                break
                
            all_people.extend(people)
            log(f"   Page {page}: {len(people)} contacts récupérés")
            
            # Si moins de 200 résultats, on a tout récupéré
            if len(people) < 200:
                break
                
            page += 1
            
        except json.JSONDecodeError:
            log(f"❌ Erreur de parsing JSON pour Copper page {page}")
            break
    
    log(f"📊 Total Copper: {len(all_people)} contacts")
    return all_people

def find_copper_person_by_email(email: str, copper_people: List[Dict] = None) -> Optional[Dict]:
    """Trouve une personne dans Copper par email"""
    if copper_people is None:
        copper_people = get_copper_people()
    
    email = normalize_email(email)
    
    for person in copper_people:
        person_emails = person.get("emails", [])
        for email_obj in person_emails:
            if normalize_email(email_obj.get("email", "")) == email:
                return person
    
    return None

def create_copper_person(email: str, fname: str = "", lname: str = "") -> bool:
    """Crée une nouvelle personne dans Copper"""
    url = f"{COPPER_API_URL}/people"
    
    # Validation
    if not email or "@" not in email:
        log(f"❌ Email invalide: {email}")
        return False
    
    # Nettoyage des données
    fname = fname.strip() if fname else ""
    lname = lname.strip() if lname else ""
    
    # Nom par défaut basé sur l'email
    default_name = email.split('@')[0].replace('.', ' ').replace('_', ' ').title()
    full_name = f"{fname} {lname}".strip() or default_name
    
    data = {
        "name": full_name,
        "emails": [{"email": email, "category": "work"}]
    }
    
    # Ajouter les noms seulement s'ils existent
    if fname:
        data["first_name"] = fname
    if lname:
        data["last_name"] = lname
    
    response = safe_request(requests.post, url, headers=COPPER_HEADERS, json=data)
    
    if response:
        log(f"✅ Création Copper réussie: {email}")
        return True
    else:
        log(f"❌ Échec création Copper: {email}")
        return False

def update_copper_person(person_id: int, email: str, fname: str = "", lname: str = "") -> bool:
    """Met à jour une personne dans Copper"""
    url = f"{COPPER_API_URL}/people/{person_id}"
    
    # Validation
    if not email or "@" not in email:
        log(f"❌ Email invalide: {email}")
        return False
    
    # Nettoyage des données
    fname = fname.strip() if fname else ""
    lname = lname.strip() if lname else ""
    
    # Nom par défaut basé sur l'email
    default_name = email.split('@')[0].replace('.', ' ').replace('_', ' ').title()
    full_name = f"{fname} {lname}".strip() or default_name
    
    data = {
        "name": full_name,
        "emails": [{"email": email, "category": "work"}]
    }
    
    # Ajouter les noms seulement s'ils existent
    if fname:
        data["first_name"] = fname
    if lname:
        data["last_name"] = lname
    
    response = safe_request(requests.put, url, headers=COPPER_HEADERS, json=data)
    
    if response:
        log(f"✅ Mise à jour Copper réussie: {email}")
        return True
    else:
        log(f"❌ Échec mise à jour Copper: {email}")
        return False

# === Fonctions API Mailchimp améliorées
def get_mailchimp_contacts(include_all_statuses: bool = False) -> List[Dict]:
    """Récupère tous les contacts Mailchimp avec pagination"""
    url = f"{MC_BASE}/lists/{MC_LIST_ID}/members"
    all_members = []
    offset = 0
    count = 1000
    
    log("🔄 Récupération des contacts Mailchimp...")
    
    while True:
        params = {
            "count": count,
            "offset": offset,
            "fields": "members.email_address,members.status,members.merge_fields"
        }
        
        # Inclure tous les statuts si demandé (pour détecter les "forgotten")
        if include_all_statuses:
            params["status"] = "subscribed,unsubscribed,cleaned,pending"
        
        response = safe_request(requests.get, url, auth=MC_AUTH, params=params)
        if not response:
            log(f"❌ Erreur lors de la récupération offset {offset}")
            break
            
        try:
            data = response.json()
            members = data.get("members", [])
            
            if not members:
                break
                
            all_members.extend(members)
            log(f"   Offset {offset}: {len(members)} contacts récupérés")
            
            # Si moins de 1000 résultats, on a tout récupéré
            if len(members) < count:
                break
                
            offset += count
            
        except json.JSONDecodeError:
            log(f"❌ Erreur de parsing JSON pour Mailchimp offset {offset}")
            break
    
    log(f"📊 Total Mailchimp: {len(all_members)} contacts")
    return all_members

def check_mailchimp_member_status(email: str) -> Dict:
    """Vérifie le statut d'un membre Mailchimp"""
    url = f"{MC_BASE}/lists/{MC_LIST_ID}/members/{get_subscriber_hash(email)}"
    
    response = safe_request(requests.get, url, auth=MC_AUTH)
    if response:
        try:
            return response.json()
        except json.JSONDecodeError:
            return {}
    return {}

def is_email_forgotten(email: str) -> bool:
    """Vérifie si un email est dans la liste des "forgotten" de Mailchimp"""
    member_info = check_mailchimp_member_status(email)
    return member_info.get("status") == "cleaned" or not member_info

def create_or_update_mailchimp_member(email: str, fname: str = "", lname: str = "", status: str = "subscribed") -> Dict:
    """Crée ou met à jour un membre Mailchimp avec gestion des erreurs détaillée"""
    
    # Vérifier d'abord si l'email est "forgotten"
    if is_email_forgotten(email):
        log(f"⚠️  Email potentiellement supprimé définitivement: {email}")
    
    url = f"{MC_BASE}/lists/{MC_LIST_ID}/members/{get_subscriber_hash(email)}"
    
    data = {
        "email_address": email,
        "status_if_new": status,
        "merge_fields": {
            "FNAME": fname.strip() if fname else "",
            "LNAME": lname.strip() if lname else ""
        }
    }
    
    response = safe_request(requests.put, url, auth=MC_AUTH, json=data)
    
    if response:
        return {"success": True, "data": response.json()}
    else:
        # Analyser l'erreur plus précisément
        error_info = {"success": False, "error": "Unknown error"}
        
        # Essayer de récupérer les détails d'erreur depuis safe_request
        try:
            # Faire une requête directe pour avoir les détails d'erreur
            direct_response = requests.put(url, auth=MC_AUTH, json=data)
            if direct_response.status_code == 400:
                error_data = direct_response.json()
                error_info["error"] = error_data.get("title", "Bad Request")
                error_info["detail"] = error_data.get("detail", "")
        except:
            pass
            
        return error_info

# === Fonctions de synchronisation améliorées
def sync_copper_to_mailchimp():
    """Synchronise Copper vers Mailchimp avec gestion des erreurs"""
    log("=== 🔄 SYNC Copper → Mailchimp ===")
    
    people = get_copper_people()
    
    synced_count = 0
    error_count = 0
    forgotten_count = 0
    sync_results = []
    
    for person in people:
        # Récupérer l'email principal
        emails = person.get("emails", [])
        if not emails:
            continue
            
        email = normalize_email(emails[0]["email"])
        
        # Filtrer seulement les emails contenant @exemple
        if not is_target_email(email):
            continue
            
        fname = person.get("first_name", "")
        lname = person.get("last_name", "")
        
        # Créer un objet de résultat pour le rapport
        result_obj = {
            'email': email,
            'direction': 'Copper → Mailchimp',
            'success': False,
            'fname': fname,
            'lname': lname,
            'forgotten_email': False,
            'resubscribe_link': '',
            'copper_tag_added': False,
            'error': ''
        }
        
        result = create_or_update_mailchimp_member(email, fname, lname)
        
        if result["success"]:
            log(f"  ✅ Sync vers Mailchimp: {email}")
            synced_count += 1
            result_obj['success'] = True
        else:
            error_type = result.get("error", "")
            if "Forgotten Email" in error_type or "cleaned" in error_type.lower():
                log(f"  🚫 Email supprimé définitivement: {email}")
                forgotten_count += 1
                result_obj['forgotten_email'] = True
                result_obj['error'] = "Email supprimé définitivement"
                
                # Générer le lien de réinscription
                resubscribe_link = generate_resubscribe_link(email)
                result_obj['resubscribe_link'] = resubscribe_link
                
                # Ajouter l'étiquette "Réinscription requise"
                tag_success = add_copper_tag(person['id'], "Réinscription requise")
                result_obj['copper_tag_added'] = tag_success
                
            else:
                log(f"  ❌ Erreur sync Mailchimp: {email} - {error_type}")
                error_count += 1
                result_obj['error'] = error_type
        
        sync_results.append(result_obj)
    
    log(f"📈 Copper → Mailchimp: {synced_count} synchronisés, {error_count} erreurs, {forgotten_count} supprimés définitivement")
    
    if forgotten_count > 0:
        log("💡 Note: Les emails supprimés définitivement doivent se réabonner manuellement")
    
    # Créer le rapport
    if sync_results:
        report_file = create_import_report(sync_results)
        log(f"📄 Rapport Copper → Mailchimp créé: {report_file}")
    
    return sync_results

def sync_mailchimp_to_copper():
    """Synchronise Mailchimp vers Copper"""
    log("=== 🔄 SYNC Mailchimp → Copper ===")
    
    # Récupérer tous les contacts Mailchimp actifs
    members = get_mailchimp_contacts()
    log(f"🔎 Vérification des contacts Mailchimp à importer...")
    
    # Récupérer tous les contacts Copper une seule fois pour optimiser
    copper_people = get_copper_people()
    
    # Créer un dictionnaire pour recherche rapide
    copper_emails = {}
    for person in copper_people:
        person_emails = person.get("emails", [])
        for email_obj in person_emails:
            email = normalize_email(email_obj.get("email", ""))
            if email:
                copper_emails[email] = person
    
    synced_count = 0
    error_count = 0
    skip_count = 0
    sync_results = []
    mailchimp_emails_to_sync = []
    
    # Pré-filtrage pour afficher le nombre de contacts éligibles
    for member in members:
        if member.get("status") == "subscribed":
            email = normalize_email(member.get("email_address", ""))
            if is_target_email(email):
                mailchimp_emails_to_sync.append(email)
    
    log(f"📋 {len(mailchimp_emails_to_sync)} contacts Mailchimp éligibles pour synchronisation")
    
    for member in members:
        # Ignorer les membres non abonnés
        if member.get("status") != "subscribed":
            continue
            
        email = normalize_email(member.get("email_address", ""))
        
        # Filtrer seulement les emails contenant @exemple
        if not is_target_email(email):
            skip_count += 1
            continue
            
        fname = member.get("merge_fields", {}).get("FNAME", "")
        lname = member.get("merge_fields", {}).get("LNAME", "")
        
        # Créer un objet de résultat pour le rapport
        result = {
            'email': email,
            'direction': 'Mailchimp → Copper',
            'success': False,
            'fname': fname,
            'lname': lname,
            'error': ''
        }
        
        # Vérifier si la personne existe déjà dans Copper
        existing = copper_emails.get(email)
        
        if existing:
            # Mettre à jour seulement si nécessaire
            needs_update = (
                existing.get("first_name", "") != fname or 
                existing.get("last_name", "") != lname
            )
            
            if needs_update:
                if update_copper_person(existing["id"], email, fname, lname):
                    log(f"  🔄 Mise à jour Copper: {email}")
                    synced_count += 1
                    result['success'] = True
                else:
                    log(f"  ❌ Erreur mise à jour Copper: {email}")
                    error_count += 1
                    result['error'] = "Erreur lors de la mise à jour du contact"
            else:
                log(f"  ⏭️  Pas de changement nécessaire: {email}")
                result['success'] = True
                result['error'] = "Aucun changement nécessaire"
        else:
            # Créer nouveau
            if create_copper_person(email, fname, lname):
                log(f"  🆕 Création Copper: {email}")
                synced_count += 1
                result['success'] = True
            else:
                log(f"  ❌ Erreur création Copper: {email}")
                error_count += 1
                result['error'] = "Erreur lors de la création du contact"
        
        sync_results.append(result)
    
    log(f"📈 Mailchimp → Copper: {synced_count} synchronisés, {error_count} erreurs, {skip_count} ignorés (hors cible)")
    
    # Créer le rapport
    if sync_results:
        report_file = create_import_report(sync_results)
        log(f"📄 Rapport Mailchimp → Copper créé: {report_file}")
    else:
        log("⚠️ Aucun contact à synchroniser de Mailchimp vers Copper")
    
    return sync_results

def analyze_data_differences():
    """Analyse les différences entre Copper et Mailchimp"""
    log("=== 📊 ANALYSE DES DIFFÉRENCES ===")
    
    # Récupérer les données des deux systèmes
    copper_people = get_copper_people()
    mailchimp_members = get_mailchimp_contacts()
    
    # Filtrer les emails @exemple
    copper_emails = set()
    for person in copper_people:
        emails = person.get("emails", [])
        if emails:
            email = normalize_email(emails[0]["email"])
            if is_target_email(email):
                copper_emails.add(email)
    
    mailchimp_emails = set()
    forgotten_emails = set()
    
    for member in mailchimp_members:
        email = normalize_email(member.get("email_address", ""))
        if is_target_email(email):
            if member.get("status") == "subscribed":
                mailchimp_emails.add(email)
            elif member.get("status") == "cleaned":
                forgotten_emails.add(email)
    
    # Calculer les différences
    copper_only = copper_emails - mailchimp_emails
    mailchimp_only = mailchimp_emails - copper_emails
    common_emails = copper_emails & mailchimp_emails
    
    log(f"📊 Emails communs: {len(common_emails)}")
    log(f"📊 Emails uniquement dans Copper: {len(copper_only)}")
    log(f"📊 Emails uniquement dans Mailchimp: {len(mailchimp_only)}")
    log(f"📊 Emails supprimés définitivement: {len(forgotten_emails)}")
    
    if copper_only:
        log("   Emails Copper uniquement:")
        for email in list(copper_only)[:10]:  # Limiter à 10 pour l'affichage
            log(f"     - {email}")
        if len(copper_only) > 10:
            log(f"     ... et {len(copper_only) - 10} autres")
    
    if mailchimp_only:
        log("   Emails Mailchimp uniquement:")
        for email in list(mailchimp_only)[:10]:  # Limiter à 10 pour l'affichage
            log(f"     - {email}")
        if len(mailchimp_only) > 10:
            log(f"     ... et {len(mailchimp_only) - 10} autres")
    
    if forgotten_emails:
        log("   Emails supprimés définitivement:")
        for email in list(forgotten_emails)[:10]:
            log(f"     - {email}")
        if len(forgotten_emails) > 10:
            log(f"     ... et {len(forgotten_emails) - 10} autres")

def check_forgotten_emails():
    """Vérifie spécifiquement les emails supprimés définitivement"""
    log("=== 🔍 VÉRIFICATION DES EMAILS SUPPRIMÉS ===")
    
    # Récupérer tous les contacts Copper avec emails @exemple
    copper_people = get_copper_people()
    target_emails = []
    
    for person in copper_people:
        emails = person.get("emails", [])
        if emails:
            email = normalize_email(emails[0]["email"])
            if is_target_email(email):
                target_emails.append(email)
    
    forgotten_emails = []
    
    for email in target_emails:
        member_info = check_mailchimp_member_status(email)
        if not member_info or member_info.get("status") == "cleaned":
            forgotten_emails.append(email)
    
    log(f"📊 Emails supprimés définitivement trouvés: {len(forgotten_emails)}")
    for email in forgotten_emails:
        log(f"  🚫 {email}")
    
    return forgotten_emails

# === Tests de connexion
def test_copper_connection():
    """Test la connexion à Copper"""
    log("🧪 Test connexion Copper...")
    url = f"{COPPER_API_URL}/users/me"
    response = safe_request(requests.get, url, headers=COPPER_HEADERS)
    
    if response:
        log("✅ Connexion à Copper réussie")
        try:
            user_data = response.json()
            log(f"   Utilisateur: {user_data.get('name', 'N/A')}")
        except json.JSONDecodeError:
            log("   Réponse valide mais parsing JSON impossible")
        return True
    else:
        log("❌ Erreur de connexion à Copper")
        return False

def test_mailchimp_connection():
    """Test la connexion à Mailchimp"""
    log("🧪 Test connexion Mailchimp...")
    url = f"{MC_BASE}/lists/{MC_LIST_ID}"
    response = safe_request(requests.get, url, auth=MC_AUTH)
    
    if response:
        log("✅ Connexion à Mailchimp réussie")
        try:
            list_data = response.json()
            log(f"   Liste: {list_data.get('name', 'N/A')}")
            log(f"   Membres: {list_data.get('stats', {}).get('member_count', 'N/A')}")
        except json.JSONDecodeError:
            log("   Réponse valide mais parsing JSON impossible")
        return True
    else:
        log("❌ Erreur de connexion à Mailchimp")
        return False

def validate_environment():
    """Valide les variables d'environnement"""
    log("🔍 Validation des variables d'environnement...")
    
    required_vars = {
        "COPPER_API_KEY": COPPER_API_KEY,
        "COPPER_API_EMAIL": COPPER_API_EMAIL,
        "MAILCHIMP_API_KEY": MC_API_KEY,
        "MAILCHIMP_DC": MC_DC,
        "MAILCHIMP_LIST_ID": MC_LIST_ID
    }
    
    missing_vars = []
    for var_name, var_value in required_vars.items():
        if not var_value:
            missing_vars.append(var_name)
    
    if missing_vars:
        log(f"❌ Variables manquantes: {', '.join(missing_vars)}")
        return False
    else:
        log("✅ Toutes les variables d'environnement sont présentes")
        return True

def reactivate_forgotten_email(email: str, fname: str = "", lname: str = "") -> bool:
    """Tente de réactiver un email supprimé définitivement"""
    url = f"{MC_BASE}/lists/{MC_LIST_ID}/members"
    
    data = {
        "email_address": email,
        "status": "pending",  # Statut en attente
        "merge_fields": {
            "FNAME": fname.strip() if fname else "",
            "LNAME": lname.strip() if lname else ""
        }
    }
    
    response = safe_request(requests.post, url, auth=MC_AUTH, json=data)
    return response is not None

def generate_resubscribe_link(email: str, list_id: str = None) -> str:
    """Génère un lien de réinscription personnalisé pour Mailchimp"""
    if not list_id:
        list_id = MC_LIST_ID
    
    # Récupérer l'ID utilisateur Mailchimp pour construire le lien correct
    try:
        # Obtenir les détails de la liste pour récupérer l'ID utilisateur
        list_url = f"{MC_BASE}/lists/{list_id}"
        response = safe_request(requests.get, list_url, auth=MC_AUTH)
        
        if response:
            list_data = response.json()
            # Essayer d'extraire l'ID utilisateur depuis l'URL de souscription
            if "subscribe_url_long" in list_data:
                url_parts = list_data["subscribe_url_long"].split("u=")
                if len(url_parts) > 1:
                    user_id = url_parts[1].split("&")[0]
                else:
                    user_id = "XXXX"
            else:
                user_id = "XXXX"
        else:
            user_id = "XXXX"
    except Exception as e:
        log(f"⚠️ Erreur lors de la récupération de l'ID utilisateur Mailchimp: {e}")
        user_id = "XXXX"
    
    # Format du lien Mailchimp avec email pré-rempli
    base_url = f"https://{MC_DC}.list-manage.com/subscribe/post?u={user_id}&id={list_id}"
    resubscribe_url = f"{base_url}&EMAIL={email}"
    
    log(f"🔗 Lien de réinscription généré pour {email}: {resubscribe_url}")
    return resubscribe_url

def add_copper_tag(person_id: int, tag_name: str) -> bool:
    """Ajoute une étiquette à un contact Copper"""
    url = f"{COPPER_API_URL}/people/{person_id}"
    
    # D'abord récupérer les tags existants
    response = safe_request(requests.get, url, headers=COPPER_HEADERS)
    if not response:
        return False
    
    try:
        person_data = response.json()
        existing_tags = person_data.get("tags", [])
        
        # Vérifier si le tag existe déjà
        if tag_name not in existing_tags:
            existing_tags.append(tag_name)
            
            # Mettre à jour avec le nouveau tag
            update_data = {"tags": existing_tags}
            update_response = safe_request(requests.put, url, headers=COPPER_HEADERS, json=update_data)
            
            if update_response:
                log(f"✅ Tag '{tag_name}' ajouté à la personne ID {person_id}")
                return True
            else:
                log(f"❌ Erreur lors de l'ajout du tag à la personne ID {person_id}")
                return False
        else:
            log(f"ℹ️  Tag '{tag_name}' déjà présent pour la personne ID {person_id}")
            return True
            
    except json.JSONDecodeError:
        log(f"❌ Erreur de parsing JSON pour la personne ID {person_id}")
        return False

def create_import_report(sync_results: List[Dict]) -> str:
    """Crée un fichier de rapport détaillé des imports"""
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    report_filename = f"import_report_{timestamp}.txt"
    
    try:
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("RAPPORT D'IMPORTATION COPPER ↔ MAILCHIMP\n")
            f.write("="*80 + "\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total d'opérations: {len(sync_results)}\n\n")
            
            # Statistiques
            success_count = sum(1 for r in sync_results if r['success'])
            error_count = len(sync_results) - success_count
            
            f.write(f"✅ Succès: {success_count}\n")
            f.write(f"❌ Erreurs: {error_count}\n")
            f.write(f"📊 Taux de réussite: {success_count/len(sync_results)*100:.1f}%\n\n")
            
            # Détails par opération
            f.write("DÉTAILS DES OPÉRATIONS:\n")
            f.write("-" * 50 + "\n")
            
            for i, result in enumerate(sync_results, 1):
                status = "✅ SUCCÈS" if result['success'] else "❌ ERREUR"
                f.write(f"{i:3d}. {status} | {result['email']}\n")
                f.write(f"     Direction: {result['direction']}\n")
                f.write(f"     Nom: {result.get('fname', 'N/A')} {result.get('lname', 'N/A')}\n")
                
                if not result['success']:
                    f.write(f"     Erreur: {result.get('error', 'Erreur inconnue')}\n")
                    
                if result.get('resubscribe_link'):
                    f.write(f"     Lien réinscription: {result['resubscribe_link']}\n")
                    
                if result.get('copper_tag_added'):
                    f.write(f"     Tag Copper ajouté: {result['copper_tag_added']}\n")
                    
                f.write("\n")
            
            # Section spéciale pour les emails supprimés définitivement
            forgotten_emails = [r for r in sync_results if r.get('forgotten_email')]
            if forgotten_emails:
                f.write("EMAILS SUPPRIMÉS DÉFINITIVEMENT:\n")
                f.write("-" * 50 + "\n")
                for result in forgotten_emails:
                    f.write(f"🚫 {result['email']}\n")
                    f.write(f"   Lien de réinscription: {result.get('resubscribe_link', 'N/A')}\n")
                    f.write(f"   Action requise: Réinscription manuelle\n\n")
        
        log(f"📄 Rapport créé: {report_filename}")
        return report_filename
        
    except Exception as e:
        log(f"❌ Erreur lors de la création du rapport: {e}")
        return ""

def handle_forgotten_emails_with_resubscribe():
    """Gère les emails supprimés définitivement avec génération de liens et étiquetage"""
    log("=== 🔄 GESTION DES EMAILS SUPPRIMÉS DÉFINITIVEMENT ===")
    
    forgotten_emails = check_forgotten_emails()
    copper_people = get_copper_people()
    
    results = []
    
    for email in forgotten_emails:
        result = {
            'email': email,
            'direction': 'Copper → Mailchimp (Réactivation)',
            'success': False,
            'forgotten_email': True,
            'resubscribe_link': '',
            'copper_tag_added': False,
            'fname': '',
            'lname': ''
        }
        
        # Trouver la personne dans Copper
        person = find_copper_person_by_email(email, copper_people)
        if person:
            result['fname'] = person.get('first_name', '')
            result['lname'] = person.get('last_name', '')
            
            # Générer le lien de réinscription
            resubscribe_link = generate_resubscribe_link(email)
            result['resubscribe_link'] = resubscribe_link
            
            # Ajouter l'étiquette "Réinscription requise"
            tag_success = add_copper_tag(person['id'], "Réinscription requise")
            result['copper_tag_added'] = tag_success
            
            # Tenter la réactivation (peut échouer pour les emails définitivement supprimés)
            reactivation_success = reactivate_forgotten_email(email, result['fname'], result['lname'])
            
            if reactivation_success:
                result['success'] = True
                log(f"✅ Email réactivé avec succès: {email}")
            else:
                result['error'] = "Réactivation impossible - Email définitivement supprimé"
                log(f"🚫 Réactivation impossible pour: {email}")
                log(f"   💡 Lien de réinscription: {resubscribe_link}")
        else:
            result['error'] = "Contact non trouvé dans Copper"
            log(f"❌ Contact non trouvé dans Copper: {email}")
        
        results.append(result)
    
    return results

# === MAIN
if __name__ == "__main__":
    log("🚀 Début de la synchronisation Copper ↔ Mailchimp")
    log(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"🎯 Mode test: emails contenant '@exemple' uniquement")
    log("")
    
    # Validation des prérequis
    if not validate_environment():
        log("❌ Arrêt du script en raison de variables manquantes")
        exit(1)
    
    # Tests de connexion
    copper_ok = test_copper_connection()
    mailchimp_ok = test_mailchimp_connection()
    
    if not (copper_ok and mailchimp_ok):
        log("❌ Arrêt du script en raison d'erreurs de connexion")
        exit(1)
    
    log("")
    
    # Synchronisations
    try:
        # Analyse préliminaire
        log("=== 🔍 ANALYSE PRÉLIMINAIRE ===")
        analyze_data_differences()
        log("")
        
        # Gestion des emails supprimés définitivement avec génération de liens
        log("=== 🔍 GESTION DES EMAILS SUPPRIMÉS ET RÉINSCRIPTION ===")
        forgotten_results = handle_forgotten_emails_with_resubscribe()
        if forgotten_results:
            forgotten_report = create_import_report(forgotten_results)
            log(f"📄 Rapport emails supprimés créé: {forgotten_report}")
        log("")
        
        # Synchronisation Mailchimp → Copper (PRIORITAIRE)
        log("=== 🔄 SYNCHRONISATION MAILCHIMP → COPPER (PRIORITAIRE) ===")
        mc_to_copper_results = sync_mailchimp_to_copper()
        log("")
        
        # Synchronisation Copper → Mailchimp
        log("=== 🔄 SYNCHRONISATION COPPER → MAILCHIMP ===")
        copper_to_mc_results = sync_copper_to_mailchimp()
        log("")
        
        # Créer un rapport global combiné
        all_results = []
        if forgotten_results:
            all_results.extend(forgotten_results)
        if mc_to_copper_results:  # Priorité aux résultats Mailchimp → Copper
            all_results.extend(mc_to_copper_results)
        if copper_to_mc_results:
            all_results.extend(copper_to_mc_results)
        
        if all_results:
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            global_report = create_import_report(all_results)
            log(f"📄 Rapport global créé: {global_report}")
        
        # Analyse finale
        log("=== 📊 ANALYSE FINALE ===")
        analyze_data_differences()
        
    except Exception as e:
        log(f"❌ Erreur critique: {e}")
        import traceback
        log(f"   Traceback: {traceback.format_exc()}")
    
    log("")
    log("🏁 Synchronisation terminée")
    log(f"📄 Log sauvegardé dans: {log_filename}")
    
    try:
        log_file.close()
    except:
        pass