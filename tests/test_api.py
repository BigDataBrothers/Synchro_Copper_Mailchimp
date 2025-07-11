"""
Tests unitaires pour les fonctions d'API (Copper et Mailchimp)
"""
import pytest
import sys
import os
from unittest.mock import patch, MagicMock, call
import requests
import json
import responses

# Ajouter le répertoire parent au path pour importer sync.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sync import (
    safe_request,
    get_target_copper_contacts,
    get_target_mailchimp_contacts,
    sync_contact_to_mailchimp,
    sync_mailchimp_to_copper,
    archive_contact,
    delete_contact,
    COPPER_HEADERS,
    MC_AUTH,
    MC_BASE,
    MC_LIST_ID,
    COPPER_API_URL
)


class TestAPIFunctions:
    """Tests pour les fonctions d'API"""
    
    def test_safe_request_success(self):
        """Test de requête réussie avec safe_request"""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        
        mock_func = MagicMock(return_value=mock_response)
        
        result = safe_request(mock_func, "test_url", headers={"test": "header"})
        
        assert result == mock_response
        mock_func.assert_called_once_with("test_url", headers={"test": "header"})
        mock_response.raise_for_status.assert_called_once()
    
    @patch('time.sleep')
    def test_safe_request_retry_then_success(self, mock_sleep):
        """Test de retry puis succès avec safe_request"""
        mock_response_success = MagicMock()
        mock_response_success.raise_for_status.return_value = None
        
        mock_func = MagicMock(side_effect=[
            requests.exceptions.RequestException("Erreur temporaire"),
            mock_response_success
        ])
        
        result = safe_request(mock_func, "test_url")
        
        assert result == mock_response_success
        assert mock_func.call_count == 2
        mock_sleep.assert_called_once_with(0.5)
    
    @patch('time.sleep')
    def test_safe_request_max_retries_exceeded(self, mock_sleep):
        """Test d'échec après max retries avec safe_request"""
        mock_func = MagicMock(side_effect=requests.exceptions.RequestException("Erreur persistante"))
        
        with pytest.raises(requests.exceptions.RequestException):
            safe_request(mock_func, "test_url")
        
        assert mock_func.call_count == 2  # max_retries = 2
        assert mock_sleep.call_count == 1


class TestCopperAPI:
    """Tests pour les fonctions API Copper"""
    
    @responses.activate
    def test_get_target_copper_contacts_success(self):
        """Test de récupération des contacts Copper avec succès"""
        # Mock de la première page
        responses.add(
            responses.POST,
            f"{COPPER_API_URL}/people/search",
            json=[
                {
                    "id": 1,
                    "first_name": "John",
                    "last_name": "Doe",
                    "emails": [{"email": "john@exemple.com"}],
                    "tags": ["VIP"]
                },
                {
                    "id": 2,
                    "first_name": "Jane",
                    "last_name": "Smith",
                    "emails": [{"email": "jane@gmail.com"}]  # Sera filtré
                }
            ],
            status=200
        )
        
        # Mock de la deuxième page (vide)
        responses.add(
            responses.POST,
            f"{COPPER_API_URL}/people/search",
            json=[],
            status=200
        )
        
        with patch('sync.TEST_MODE', True):
            contacts = get_target_copper_contacts()
        
        # Seul le contact @exemple devrait être retourné
        assert len(contacts) == 1
        assert contacts[0]["emails"][0]["email"] == "john@exemple.com"
    
    @responses.activate
    def test_get_target_copper_contacts_empty(self):
        """Test de récupération sans contacts cibles"""
        responses.add(
            responses.POST,
            f"{COPPER_API_URL}/people/search",
            json=[],
            status=200
        )
        
        with patch('sync.TEST_MODE', True):
            contacts = get_target_copper_contacts()
        
        assert len(contacts) == 0
    
    @responses.activate
    def test_get_target_copper_contacts_api_error(self):
        """Test de gestion d'erreur API Copper"""
        responses.add(
            responses.POST,
            f"{COPPER_API_URL}/people/search",
            json={"error": "Unauthorized"},
            status=401
        )
        
        with patch('sync.TEST_MODE', True):
            with pytest.raises(requests.exceptions.HTTPError):
                get_target_copper_contacts()


class TestMailchimpAPI:
    """Tests pour les fonctions API Mailchimp"""
    
    @responses.activate
    def test_get_target_mailchimp_contacts_success(self):
        """Test de récupération des contacts Mailchimp avec succès"""
        responses.add(
            responses.GET,
            f"{MC_BASE}/lists/{MC_LIST_ID}/members",
            json={
                "members": [
                    {
                        "email_address": "john@exemple.com",
                        "merge_fields": {"FNAME": "John", "LNAME": "Doe"},
                        "status": "subscribed"
                    },
                    {
                        "email_address": "jane@gmail.com",  # Sera filtré
                        "merge_fields": {"FNAME": "Jane", "LNAME": "Smith"},
                        "status": "subscribed"
                    }
                ]
            },
            status=200
        )
        
        with patch('sync.TEST_MODE', True):
            members = get_target_mailchimp_contacts()
        
        # Seul le membre @exemple devrait être retourné
        assert len(members) == 1
        assert members[0]["email_address"] == "john@exemple.com"
    
    @responses.activate
    def test_sync_contact_to_mailchimp_success(self):
        """Test de synchronisation d'un contact vers Mailchimp"""
        contact = {
            "first_name": "John",
            "last_name": "Doe",
            "emails": [{"email": "john@exemple.com"}]
        }
        
        tags = ["VIP", "Client"]
        
        # Mock des réponses Mailchimp
        responses.add(
            responses.PUT,
            f"{MC_BASE}/lists/{MC_LIST_ID}/members/d9298b228e52f03878c1630fd434e89d",
            json={"email_address": "john@exemple.com"},
            status=200
        )
        
        responses.add(
            responses.POST,
            f"{MC_BASE}/lists/{MC_LIST_ID}/members/d9298b228e52f03878c1630fd434e89d/tags",
            json={"tags": [{"name": "VIP", "status": "active"}]},
            status=200
        )
        
        result = sync_contact_to_mailchimp(contact, tags)
        
        assert result == True
        assert len(responses.calls) == 2
    
    @responses.activate
    def test_sync_contact_to_mailchimp_no_email(self):
        """Test de synchronisation d'un contact sans email"""
        contact = {
            "first_name": "John",
            "last_name": "Doe",
            "emails": []  # Pas d'email
        }
        
        result = sync_contact_to_mailchimp(contact)
        
        assert result == False
        assert len(responses.calls) == 0
    
    @responses.activate
    def test_sync_contact_to_mailchimp_api_error(self):
        """Test de gestion d'erreur lors de la synchronisation"""
        contact = {
            "first_name": "John",
            "last_name": "Doe",
            "emails": [{"email": "john@exemple.com"}]
        }
        
        responses.add(
            responses.PUT,
            f"{MC_BASE}/lists/{MC_LIST_ID}/members/d9298b228e52f03878c1630fd434e89d",
            json={"error": "Invalid email"},
            status=400
        )
        
        result = sync_contact_to_mailchimp(contact)
        
        assert result == False


class TestContactManagement:
    """Tests pour la gestion des contacts (archivage, suppression)"""
    
    @responses.activate
    def test_archive_contact_success(self):
        """Test d'archivage d'un contact"""
        contact = {
            "email": "john@exemple.com",
            "copper_id": 123,
            "name": "John Doe"
        }
        
        # Mock pour récupérer le contact actuel
        responses.add(
            responses.GET,
            f"{COPPER_API_URL}/people/123",
            json={
                "id": 123,
                "tags": ["VIP", "🗑 À SUPPRIMER"]
            },
            status=200
        )
        
        # Mock pour mettre à jour le contact
        responses.add(
            responses.PUT,
            f"{COPPER_API_URL}/people/123",
            json={"id": 123},
            status=200
        )
        
        # Mock pour désabonner de Mailchimp
        responses.add(
            responses.PATCH,
            f"{MC_BASE}/lists/{MC_LIST_ID}/members/d9298b228e52f03878c1630fd434e89d",
            json={"status": "unsubscribed"},
            status=200
        )
        
        # Ne devrait pas lever d'exception
        archive_contact(contact)
        
        assert len(responses.calls) == 3
    
    @responses.activate
    def test_delete_contact_success(self):
        """Test de suppression d'un contact"""
        contact = {
            "email": "john@exemple.com",
            "copper_id": 123,
            "name": "John Doe"
        }
        
        # Mock pour supprimer de Mailchimp
        responses.add(
            responses.DELETE,
            f"{MC_BASE}/lists/{MC_LIST_ID}/members/d9298b228e52f03878c1630fd434e89d",
            status=204
        )
        
        # Mock pour supprimer de Copper
        responses.add(
            responses.DELETE,
            f"{COPPER_API_URL}/people/123",
            status=204
        )
        
        # Ne devrait pas lever d'exception
        delete_contact(contact)
        
        assert len(responses.calls) == 2
    
    @responses.activate
    def test_sync_mailchimp_to_copper_success(self):
        """Test de synchronisation Mailchimp vers Copper"""
        mc_members = [
            {
                "email_address": "new@exemple.com",
                "merge_fields": {"FNAME": "New", "LNAME": "User"}
            }
        ]
        
        copper_contacts_by_email = {}  # Pas de contact existant
        
        # Mock pour créer le contact dans Copper
        responses.add(
            responses.POST,
            f"{COPPER_API_URL}/people",
            json={"id": 456},
            status=201
        )
        
        synced_count = sync_mailchimp_to_copper(mc_members, copper_contacts_by_email)
        
        assert synced_count == 1
        assert len(responses.calls) == 1
    
    def test_sync_mailchimp_to_copper_existing_contact(self):
        """Test de synchronisation avec contact existant"""
        mc_members = [
            {
                "email_address": "existing@exemple.com",
                "merge_fields": {"FNAME": "Existing", "LNAME": "User"}
            }
        ]
        
        copper_contacts_by_email = {
            "existing@exemple.com": {"id": 123}
        }
        
        synced_count = sync_mailchimp_to_copper(mc_members, copper_contacts_by_email)
        
        assert synced_count == 0  # Pas de synchronisation car contact existant
    
    def test_sync_mailchimp_to_copper_no_name(self):
        """Test de synchronisation sans nom"""
        mc_members = [
            {
                "email_address": "noname@exemple.com",
                "merge_fields": {}  # Pas de nom
            }
        ]
        
        copper_contacts_by_email = {}
        
        synced_count = sync_mailchimp_to_copper(mc_members, copper_contacts_by_email)
        
        assert synced_count == 0  # Pas de synchronisation car pas de nom


class TestIntegration:
    """Tests d'intégration simulant des scénarios réels"""
    
    @responses.activate
    def test_full_sync_scenario(self):
        """Test d'un scénario complet de synchronisation"""
        # Données de test
        copper_contacts = [
            {
                "id": 1,
                "first_name": "John",
                "last_name": "Doe",
                "emails": [{"email": "john@exemple.com"}],
                "tags": ["VIP"]
            }
        ]
        
        mc_members = [
            {
                "email_address": "jane@exemple.com",
                "merge_fields": {"FNAME": "Jane", "LNAME": "Smith"}
            }
        ]
        
        # Mock des appels API
        responses.add(
            responses.PUT,
            f"{MC_BASE}/lists/{MC_LIST_ID}/members/d9298b228e52f03878c1630fd434e89d",
            json={"email_address": "john@exemple.com"},
            status=200
        )
        
        responses.add(
            responses.POST,
            f"{MC_BASE}/lists/{MC_LIST_ID}/members/d9298b228e52f03878c1630fd434e89d/tags",
            json={"tags": [{"name": "VIP", "status": "active"}]},
            status=200
        )
        
        responses.add(
            responses.POST,
            f"{COPPER_API_URL}/people",
            json={"id": 456},
            status=201
        )
        
        # Test de synchronisation Copper → Mailchimp
        result1 = sync_contact_to_mailchimp(copper_contacts[0], copper_contacts[0]["tags"])
        assert result1 == True
        
        # Test de synchronisation Mailchimp → Copper
        result2 = sync_mailchimp_to_copper(mc_members, {})
        assert result2 == 1
        
        # Vérification des appels API
        assert len(responses.calls) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
