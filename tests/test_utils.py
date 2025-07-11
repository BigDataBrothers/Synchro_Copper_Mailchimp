"""
Tests unitaires pour les fonctions utilitaires du module sync.py
"""
import pytest
import sys
import os
from unittest.mock import patch, MagicMock, mock_open
import json
import hashlib

# Ajouter le répertoire parent au path pour importer sync.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sync import (
    normalize_email, 
    is_target_email, 
    is_delete_tag_robust,
    is_inactive_tag,
    get_subscriber_hash,
    normalize_contact_data,
    contacts_are_identical,
    add_operation_detail,
    operation_details
)


class TestUtilityFunctions:
    """Tests pour les fonctions utilitaires"""
    
    def test_normalize_email_valid(self):
        """Test de normalisation d'emails valides"""
        assert normalize_email("TEST@EXAMPLE.COM") == "test@example.com"
        assert normalize_email("  user@domain.org  ") == "user@domain.org"
        assert normalize_email("User.Name@Domain.Net") == "user.name@domain.net"
    
    def test_normalize_email_empty(self):
        """Test de normalisation d'emails vides"""
        assert normalize_email("") == ""
        assert normalize_email("   ") == ""
    
    def test_is_target_email_valid(self):
        """Test de détection des emails cibles"""
        assert is_target_email("test@exemple.com") == True
        assert is_target_email("user@EXEMPLE.org") == True
        assert is_target_email("contact@exemple.fr") == True
        assert is_target_email("normal@gmail.com") == False
        assert is_target_email("work@company.com") == False
    
    def test_is_delete_tag_robust_valid(self):
        """Test de détection des tags de suppression"""
        # Tags français
        assert is_delete_tag_robust("🗑 À SUPPRIMER") == True
        assert is_delete_tag_robust("SUPPRIMER") == True
        assert is_delete_tag_robust("  supprimer  ") == True
        assert is_delete_tag_robust("A SUPPRIMER") == True
        
        # Tags anglais
        assert is_delete_tag_robust("DELETE") == True
        assert is_delete_tag_robust("remove") == True
        assert is_delete_tag_robust("🗑 Delete this") == True
        
        # Tags normaux
        assert is_delete_tag_robust("Client VIP") == False
        assert is_delete_tag_robust("Actif") == False
        assert is_delete_tag_robust("") == False
        assert is_delete_tag_robust(None) == False
    
    def test_is_inactive_tag_valid(self):
        """Test de détection des tags inactifs"""
        assert is_inactive_tag("📥 INACTIF") == True
        assert is_inactive_tag("INACTIF") == True
        assert is_inactive_tag("  inactive  ") == True
        assert is_inactive_tag("ARCHIVED") == True
        assert is_inactive_tag("📥 Archived") == True
        
        # Tags normaux
        assert is_inactive_tag("Actif") == False
        assert is_inactive_tag("Client") == False
        assert is_inactive_tag("") == False
        assert is_inactive_tag(None) == False
    
    def test_get_subscriber_hash(self):
        """Test de génération du hash subscriber"""
        email = "test@example.com"
        expected_hash = hashlib.md5(email.lower().encode()).hexdigest()
        assert get_subscriber_hash(email) == expected_hash
        
        # Test avec email en majuscules
        assert get_subscriber_hash("TEST@EXAMPLE.COM") == expected_hash
    
    def test_normalize_contact_data(self):
        """Test de normalisation des données de contact"""
        contact_data = {
            "first_name": "  John  ",
            "last_name": "  Doe  ",
            "email": "JOHN.DOE@EXAMPLE.COM"
        }
        
        normalized = normalize_contact_data(contact_data)
        
        assert normalized["first_name"] == "John"
        assert normalized["last_name"] == "Doe"
        assert normalized["email"] == "john.doe@example.com"
    
    def test_normalize_contact_data_empty(self):
        """Test de normalisation avec données vides"""
        contact_data = {
            "first_name": None,
            "last_name": "",
            "email": ""
        }
        
        normalized = normalize_contact_data(contact_data)
        
        assert normalized["first_name"] == ""
        assert normalized["last_name"] == ""
        assert normalized["email"] == ""
    
    def test_contacts_are_identical(self):
        """Test de comparaison de contacts identiques"""
        copper_contact = {
            "first_name": "John",
            "last_name": "Doe",
            "emails": [{"email": "john.doe@example.com"}]
        }
        
        mailchimp_member = {
            "email_address": "john.doe@example.com",
            "merge_fields": {
                "FNAME": "John",
                "LNAME": "Doe"
            }
        }
        
        assert contacts_are_identical(copper_contact, mailchimp_member) == True
    
    def test_contacts_are_different(self):
        """Test de comparaison de contacts différents"""
        copper_contact = {
            "first_name": "John",
            "last_name": "Doe",
            "emails": [{"email": "john.doe@example.com"}]
        }
        
        mailchimp_member = {
            "email_address": "john.doe@example.com",
            "merge_fields": {
                "FNAME": "Jane",  # Prénom différent
                "LNAME": "Doe"
            }
        }
        
        assert contacts_are_identical(copper_contact, mailchimp_member) == False
    
    def test_add_operation_detail(self):
        """Test d'ajout de détails d'opération"""
        # Vider la liste globale avant le test
        global operation_details
        operation_details.clear()
        
        add_operation_detail(
            email="test@example.com",
            name="John Doe",
            direction="Copper → Mailchimp",
            success=True,
            tags=["VIP", "Client"]
        )
        
        assert len(operation_details) == 1
        assert operation_details[0]["email"] == "test@example.com"
        assert operation_details[0]["name"] == "John Doe"
        assert operation_details[0]["direction"] == "Copper → Mailchimp"
        assert operation_details[0]["success"] == True
        assert operation_details[0]["tags"] == ["VIP", "Client"]
    
    def test_add_operation_detail_error(self):
        """Test d'ajout de détails d'opération avec erreur"""
        # Vider la liste globale avant le test
        global operation_details
        operation_details.clear()
        
        add_operation_detail(
            email="error@example.com",
            name="Error User",
            direction="Copper → Mailchimp",
            success=False,
            error="API Error 500"
        )
        
        assert len(operation_details) == 1
        assert operation_details[0]["success"] == False
        assert operation_details[0]["error"] == "API Error 500"


class TestEdgeCases:
    """Tests pour les cas limites et les données malformées"""
    
    def test_normalize_email_special_characters(self):
        """Test avec des caractères spéciaux dans l'email"""
        # Ces emails devraient être traités sans erreur
        test_emails = [
            "user+tag@example.com",
            "user.name@example.com",
            "user_name@example.com",
            "123@example.com"
        ]
        
        for email in test_emails:
            normalized = normalize_email(email)
            assert normalized == email.lower()
    
    def test_is_delete_tag_robust_edge_cases(self):
        """Test avec des cas limites pour les tags de suppression"""
        # Types de données inattendus
        assert is_delete_tag_robust(123) == False
        assert is_delete_tag_robust([]) == False
        assert is_delete_tag_robust({}) == False
        
        # Strings avec des caractères spéciaux
        assert is_delete_tag_robust("🗑️ SUPPRIMER CLIENT") == True
        assert is_delete_tag_robust("DELETE_USER") == True
        assert is_delete_tag_robust("remove-contact") == True
    
    def test_contacts_are_identical_missing_fields(self):
        """Test de comparaison avec des champs manquants"""
        copper_contact = {
            "emails": [{"email": "test@example.com"}]
            # Pas de first_name, last_name
        }
        
        mailchimp_member = {
            "email_address": "test@example.com",
            "merge_fields": {}
            # Pas de FNAME, LNAME
        }
        
        # Devrait être considéré comme identique (champs vides)
        assert contacts_are_identical(copper_contact, mailchimp_member) == True
    
    def test_contacts_are_identical_empty_emails(self):
        """Test avec des emails vides"""
        copper_contact = {
            "first_name": "John",
            "last_name": "Doe",
            "emails": []  # Pas d'email
        }
        
        mailchimp_member = {
            "email_address": "",
            "merge_fields": {
                "FNAME": "John",
                "LNAME": "Doe"
            }
        }
        
        assert contacts_are_identical(copper_contact, mailchimp_member) == True


class TestTagDetection:
    """Tests spécialisés pour la détection des tags"""
    
    @pytest.mark.parametrize("tag,expected", [
        ("🗑 À SUPPRIMER", True),
        ("SUPPRIMER", True),
        ("supprimer", True),
        ("A SUPPRIMER", True),
        ("DELETE", True),
        ("delete", True),
        ("REMOVE", True),
        ("remove", True),
        ("🗑 Delete this contact", True),
        ("Please DELETE", True),
        ("Client VIP", False),
        ("Actif", False),
        ("Prospect", False),
        ("", False),
        (None, False),
    ])
    def test_delete_tag_detection(self, tag, expected):
        """Test paramétré pour la détection des tags de suppression"""
        assert is_delete_tag_robust(tag) == expected
    
    @pytest.mark.parametrize("tag,expected", [
        ("📥 INACTIF", True),
        ("INACTIF", True),
        ("inactif", True),
        ("INACTIVE", True),
        ("inactive", True),
        ("ARCHIVED", True),
        ("archived", True),
        ("📥 Archived contact", True),
        ("Client Actif", False),
        ("VIP", False),
        ("", False),
        (None, False),
    ])
    def test_inactive_tag_detection(self, tag, expected):
        """Test paramétré pour la détection des tags inactifs"""
        assert is_inactive_tag(tag) == expected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
