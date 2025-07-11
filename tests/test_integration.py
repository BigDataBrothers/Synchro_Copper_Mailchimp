"""
Tests d'intégration pour tester le workflow complet
"""
import pytest
import sys
import os
from unittest.mock import patch, MagicMock
import json
import responses

# Ajouter le répertoire parent au path pour importer sync.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sync import main, operation_details


@pytest.mark.integration
class TestIntegrationWorkflow:
    """Tests d'intégration pour le workflow complet"""
    
    @responses.activate
    @patch('sync.TEST_MODE', True)
    @patch('builtins.input', return_value='i')  # Ignorer les contacts marqués
    @patch('sync.log_file')
    @patch('sync.report_file')
    def test_complete_sync_workflow_success(self, mock_report_file, mock_log_file, mock_input):
        """Test d'un workflow complet de synchronisation avec succès"""
        # Configuration des mocks de fichiers
        mock_log_file.write = MagicMock()
        mock_log_file.flush = MagicMock()
        mock_log_file.close = MagicMock()
        
        mock_report_file.write = MagicMock()
        mock_report_file.flush = MagicMock()
        mock_report_file.close = MagicMock()
        
        # Mock des réponses API Copper (récupération des contacts)
        responses.add(
            responses.POST,
            "https://api.copper.com/developer_api/v1/people/search",
            json=[
                {
                    "id": 1,
                    "first_name": "John",
                    "last_name": "Doe",
                    "emails": [{"email": "john@exemple.com"}],
                    "tags": ["VIP", "Client"]
                },
                {
                    "id": 2,
                    "first_name": "Jane",
                    "last_name": "Smith",
                    "emails": [{"email": "jane@exemple.com"}],
                    "tags": ["🗑 À SUPPRIMER"]  # Contact marqué
                }
            ],
            status=200
        )
        
        # Mock de la page vide (fin de pagination)
        responses.add(
            responses.POST,
            "https://api.copper.com/developer_api/v1/people/search",
            json=[],
            status=200
        )
         # Mock des réponses API Mailchimp (récupération des membres)
        responses.add(
            responses.GET,
            "https://us7.api.mailchimp.com/3.0/lists/7903d14477/members",
            json={
                "members": [
                    {
                        "email_address": "existing@exemple.com",
                        "merge_fields": {"FNAME": "Existing", "LNAME": "User"},
                        "status": "subscribed"
                    }
                ]
            },
            status=200
        )

        # Mock de synchronisation vers Mailchimp
        responses.add(
            responses.PUT,
            "https://us7.api.mailchimp.com/3.0/lists/7903d14477/members/5d41402abc4b2a76b9719d911017c592",
            json={"email_address": "john@exemple.com"},
            status=200
        )

        # Mock de synchronisation des tags
        responses.add(
            responses.POST,
            "https://us7.api.mailchimp.com/3.0/lists/7903d14477/members/5d41402abc4b2a76b9719d911017c592/tags",
            json={"tags": [{"name": "VIP", "status": "active"}]},
            status=200
        )
        
        # Mock de création de contact dans Copper
        responses.add(
            responses.POST,
            "https://api.copper.com/developer_api/v1/people",
            json={"id": 999},
            status=201
        )
        
        # Vider les détails d'opération avant le test
        operation_details.clear()
        
        # Exécuter le workflow principal
        main()
        
        # Vérifications
        assert len(responses.calls) >= 4  # Au moins 4 appels API
        
        # Vérifier que les fichiers ont été écrits
        mock_log_file.write.assert_called()
        mock_log_file.close.assert_called()
        mock_report_file.write.assert_called()
        mock_report_file.close.assert_called()
    
    @responses.activate
    @patch('sync.TEST_MODE', True)
    @patch('builtins.input', return_value='i')
    @patch('sync.log_file')
    @patch('sync.report_file')
    def test_complete_sync_workflow_with_errors(self, mock_report_file, mock_log_file, mock_input):
        """Test d'un workflow complet avec des erreurs API"""
        # Configuration des mocks de fichiers
        mock_log_file.write = MagicMock()
        mock_log_file.flush = MagicMock()
        mock_log_file.close = MagicMock()
        
        mock_report_file.write = MagicMock()
        mock_report_file.flush = MagicMock()
        mock_report_file.close = MagicMock()
        
        # Mock des réponses API Copper (succès)
        responses.add(
            responses.POST,
            "https://api.copper.com/developer_api/v1/people/search",
            json=[
                {
                    "id": 1,
                    "first_name": "John",
                    "last_name": "Doe",
                    "emails": [{"email": "john@exemple.com"}],
                    "tags": ["VIP"]
                }
            ],
            status=200
        )
        
        responses.add(
            responses.POST,
            "https://api.copper.com/developer_api/v1/people/search",
            json=[],
            status=200
        )
         # Mock des réponses API Mailchimp (succès)
        responses.add(
            responses.GET,
            "https://us7.api.mailchimp.com/3.0/lists/7903d14477/members",
            json={"members": []},
            status=200
        )

        # Mock de synchronisation vers Mailchimp (erreur)
        responses.add(
            responses.PUT,
            "https://us7.api.mailchimp.com/3.0/lists/7903d14477/members/5d41402abc4b2a76b9719d911017c592",
            json={"error": "Invalid email"},
            status=400
        )
        
        # Vider les détails d'opération avant le test
        operation_details.clear()
        
        # Exécuter le workflow principal
        main()
        
        # Vérifications
        assert len(responses.calls) >= 3
        
        # Vérifier que les fichiers ont été écrits même en cas d'erreur
        mock_log_file.write.assert_called()
        mock_log_file.close.assert_called()
        mock_report_file.write.assert_called()
        mock_report_file.close.assert_called()
    
    @responses.activate
    @patch('sync.TEST_MODE', True)
    @patch('builtins.input', side_effect=['g', 'a'])  # Archiver en groupe
    @patch('sync.log_file')
    @patch('sync.report_file')
    def test_workflow_with_marked_contacts_archive(self, mock_report_file, mock_log_file, mock_input):
        """Test du workflow avec archivage de contacts marqués"""
        # Configuration des mocks de fichiers
        mock_log_file.write = MagicMock()
        mock_log_file.flush = MagicMock()
        mock_log_file.close = MagicMock()
        
        mock_report_file.write = MagicMock()
        mock_report_file.flush = MagicMock()
        mock_report_file.close = MagicMock()
        
        # Mock des réponses API Copper (contacts marqués)
        responses.add(
            responses.POST,
            "https://api.copper.com/developer_api/v1/people/search",
            json=[
                {
                    "id": 1,
                    "first_name": "Marked",
                    "last_name": "User",
                    "emails": [{"email": "marked@exemple.com"}],
                    "tags": ["🗑 À SUPPRIMER", "Client"]
                }
            ],
            status=200
        )
        
        responses.add(
            responses.POST,
            "https://api.copper.com/developer_api/v1/people/search",
            json=[],
            status=200
        )
         # Mock des réponses API Mailchimp
        responses.add(
            responses.GET,
            "https://us7.api.mailchimp.com/3.0/lists/7903d14477/members",
            json={"members": []},
            status=200
        )

        # Mock pour l'archivage - récupération du contact
        responses.add(
            responses.GET,
            "https://api.copper.com/developer_api/v1/people/1",
            json={
                "id": 1,
                "tags": ["🗑 À SUPPRIMER", "Client"]
            },
            status=200
        )
        
        # Mock pour l'archivage - mise à jour du contact
        responses.add(
            responses.PUT,
            "https://api.copper.com/developer_api/v1/people/1",
            json={"id": 1},
            status=200
        )
        
        # Mock pour l'archivage - désabonnement Mailchimp
        responses.add(
            responses.PATCH,
            "https://us7.api.mailchimp.com/3.0/lists/7903d14477/members/2b10ad56e3c7a2d2e5e5e5e5e5e5e5e5",
            json={"status": "unsubscribed"},
            status=200
        )
        
        # Vider les détails d'opération avant le test
        operation_details.clear()
        
        # Exécuter le workflow principal
        main()
        
        # Vérifications
        assert len(responses.calls) >= 5  # Appels pour archivage inclus
        
        # Vérifier que les fichiers ont été écrits
        mock_log_file.write.assert_called()
        mock_log_file.close.assert_called()
        mock_report_file.write.assert_called()
        mock_report_file.close.assert_called()
    
    @responses.activate
    @patch('sync.TEST_MODE', True)
    @patch('builtins.input', side_effect=['g', 's'])  # Supprimer en groupe
    @patch('sync.log_file')
    @patch('sync.report_file')
    def test_workflow_with_marked_contacts_delete(self, mock_report_file, mock_log_file, mock_input):
        """Test du workflow avec suppression de contacts marqués"""
        # Configuration des mocks de fichiers
        mock_log_file.write = MagicMock()
        mock_log_file.flush = MagicMock()
        mock_log_file.close = MagicMock()
        
        mock_report_file.write = MagicMock()
        mock_report_file.flush = MagicMock()
        mock_report_file.close = MagicMock()
        
        # Mock des réponses API Copper (contacts marqués)
        responses.add(
            responses.POST,
            "https://api.copper.com/developer_api/v1/people/search",
            json=[
                {
                    "id": 1,
                    "first_name": "ToDelete",
                    "last_name": "User",
                    "emails": [{"email": "delete@exemple.com"}],
                    "tags": ["🗑 À SUPPRIMER"]
                }
            ],
            status=200
        )
        
        responses.add(
            responses.POST,
            "https://api.copper.com/developer_api/v1/people/search",
            json=[],
            status=200
        )
         # Mock des réponses API Mailchimp
        responses.add(
            responses.GET,
            "https://us7.api.mailchimp.com/3.0/lists/7903d14477/members",
            json={"members": []},
            status=200
        )

        # Mock pour la suppression - Mailchimp
        responses.add(
            responses.DELETE,
            "https://us7.api.mailchimp.com/3.0/lists/7903d14477/members/8b3d1e1c5d5b5e5e5e5e5e5e5e5e5e5e",
            status=204
        )
        
        # Mock pour la suppression - Copper
        responses.add(
            responses.DELETE,
            "https://api.copper.com/developer_api/v1/people/1",
            status=204
        )
        
        # Vider les détails d'opération avant le test
        operation_details.clear()
        
        # Exécuter le workflow principal
        main()
        
        # Vérifications
        assert len(responses.calls) >= 4  # Appels pour suppression inclus
        
        # Vérifier que les fichiers ont été écrits
        mock_log_file.write.assert_called()
        mock_log_file.close.assert_called()
        mock_report_file.write.assert_called()
        mock_report_file.close.assert_called()
    
    @responses.activate
    @patch('sync.TEST_MODE', True)
    @patch('builtins.input', return_value='i')
    @patch('sync.log_file')
    @patch('sync.report_file')
    def test_workflow_no_target_contacts(self, mock_report_file, mock_log_file, mock_input):
        """Test du workflow sans contacts cibles"""
        # Configuration des mocks de fichiers
        mock_log_file.write = MagicMock()
        mock_log_file.flush = MagicMock()
        mock_log_file.close = MagicMock()
        
        mock_report_file.write = MagicMock()
        mock_report_file.flush = MagicMock()
        mock_report_file.close = MagicMock()
        
        # Mock des réponses API Copper (pas de contacts @exemple)
        responses.add(
            responses.POST,
            "https://api.copper.com/developer_api/v1/people/search",
            json=[
                {
                    "id": 1,
                    "first_name": "John",
                    "last_name": "Doe",
                    "emails": [{"email": "john@gmail.com"}],  # Pas @exemple
                    "tags": ["VIP"]
                }
            ],
            status=200
        )
        
        responses.add(
            responses.POST,
            "https://api.copper.com/developer_api/v1/people/search",
            json=[],
            status=200
        )
        
        # Mock des réponses API Mailchimp (pas de membres @exemple)
        responses.add(
            responses.GET,
            "https://us7.api.mailchimp.com/3.0/lists/7903d14477/members",
            json={
                "members": [
                    {
                        "email_address": "existing@gmail.com",  # Pas @exemple
                        "merge_fields": {"FNAME": "Existing", "LNAME": "User"},
                        "status": "subscribed"
                    }
                ]
            },
            status=200
        )
        
        # Vider les détails d'opération avant le test
        operation_details.clear()
        
        # Exécuter le workflow principal
        main()
        
        # Vérifications
        assert len(responses.calls) >= 2  # Au moins les appels de récupération
        
        # Vérifier que les fichiers ont été écrits
        mock_log_file.write.assert_called()
        mock_log_file.close.assert_called()
        # Note: pas de rapport généré quand aucun contact à traiter
    
    @responses.activate
    @patch('sync.TEST_MODE', False)  # Mode production
    @patch('builtins.input', return_value='i')
    @patch('sync.log_file')
    @patch('sync.report_file')
    def test_workflow_production_mode(self, mock_report_file, mock_log_file, mock_input):
        """Test du workflow en mode production"""
        # Configuration des mocks de fichiers
        mock_log_file.write = MagicMock()
        mock_log_file.flush = MagicMock()
        mock_log_file.close = MagicMock()
        
        mock_report_file.write = MagicMock()
        mock_report_file.flush = MagicMock()
        mock_report_file.close = MagicMock()
        
        # Mock des réponses API Copper (tous les contacts)
        responses.add(
            responses.POST,
            "https://api.copper.com/developer_api/v1/people/search",
            json=[
                {
                    "id": 1,
                    "first_name": "John",
                    "last_name": "Doe",
                    "emails": [{"email": "john@example.com"}],
                    "tags": ["VIP"]
                }
            ],
            status=200
        )
        
        responses.add(
            responses.POST,
            "https://api.copper.com/developer_api/v1/people/search",
            json=[],
            status=200
        )
         # Mock des réponses API Mailchimp (tous les membres)
        responses.add(
            responses.GET,
            "https://us7.api.mailchimp.com/3.0/lists/7903d14477/members",
            json={"members": []},
            status=200
        )

        # Mock de synchronisation vers Mailchimp
        responses.add(
            responses.PUT,
            "https://us7.api.mailchimp.com/3.0/lists/7903d14477/members/5d41402abc4b2a76b9719d911017c592",
            json={"email_address": "john@example.com"},
            status=200
        )

        # Mock de synchronisation des tags
        responses.add(
            responses.POST,
            "https://us7.api.mailchimp.com/3.0/lists/7903d14477/members/5d41402abc4b2a76b9719d911017c592/tags",
            json={"tags": [{"name": "VIP", "status": "active"}]},
            status=200
        )
        
        # Vider les détails d'opération avant le test
        operation_details.clear()
        
        # Exécuter le workflow principal
        main()
        
        # Vérifications
        assert len(responses.calls) >= 2  # Au moins les appels de récupération
        
        # Vérifier que les fichiers ont été écrits
        mock_log_file.write.assert_called()
        mock_log_file.close.assert_called()
        # Note: pas de rapport généré quand aucun contact à traiter


@pytest.mark.integration
class TestEndToEndScenarios:
    """Tests de scénarios end-to-end"""
    
    @responses.activate
    @patch('sync.TEST_MODE', True)
    @patch('builtins.input', return_value='i')
    @patch('sync.log_file')
    @patch('sync.report_file')
    def test_bidirectional_sync_complete(self, mock_report_file, mock_log_file, mock_input):
        """Test complet de synchronisation bidirectionnelle"""
        # Configuration des mocks de fichiers
        mock_log_file.write = MagicMock()
        mock_log_file.flush = MagicMock()
        mock_log_file.close = MagicMock()
        
        mock_report_file.write = MagicMock()
        mock_report_file.flush = MagicMock()
        mock_report_file.close = MagicMock()
        
        # Scénario : 
        # - Contact A existe dans Copper mais pas dans Mailchimp
        # - Contact B existe dans Mailchimp mais pas dans Copper
        # - Contact C existe dans les deux (identique)
        
        # Mock des réponses API Copper
        responses.add(
            responses.POST,
            "https://api.copper.com/developer_api/v1/people/search",
            json=[
                {
                    "id": 1,
                    "first_name": "Alice",
                    "last_name": "Cooper",
                    "emails": [{"email": "alice@exemple.com"}],
                    "tags": ["VIP"]
                },
                {
                    "id": 3,
                    "first_name": "Charlie",
                    "last_name": "Brown",
                    "emails": [{"email": "charlie@exemple.com"}],
                    "tags": ["Client"]
                }
            ],
            status=200
        )
        
        responses.add(
            responses.POST,
            "https://api.copper.com/developer_api/v1/people/search",
            json=[],
            status=200
        )
         # Mock des réponses API Mailchimp
        responses.add(
            responses.GET,
            "https://us7.api.mailchimp.com/3.0/lists/7903d14477/members",
            json={
                "members": [
                    {
                        "email_address": "bob@exemple.com",
                        "merge_fields": {"FNAME": "Bob", "LNAME": "Dylan"},
                        "status": "subscribed"
                    },
                    {
                        "email_address": "charlie@exemple.com",
                        "merge_fields": {"FNAME": "Charlie", "LNAME": "Brown"},
                        "status": "subscribed"
                    }
                ]
            },
            status=200
        )

        # Mock de synchronisation Alice vers Mailchimp
        responses.add(
            responses.PUT,
            "https://us7.api.mailchimp.com/3.0/lists/7903d14477/members/cd7956456b781c0585bb3ca0ac4fa78e",
            json={"email_address": "alice@exemple.com"},
            status=200
        )

        responses.add(
            responses.POST,
            "https://us7.api.mailchimp.com/3.0/lists/7903d14477/members/cd7956456b781c0585bb3ca0ac4fa78e/tags",
            json={"tags": [{"name": "VIP", "status": "active"}]},
            status=200
        )

        # Mock de synchronisation Charlie vers Mailchimp (mise à jour)
        responses.add(
            responses.PUT,
            "https://us7.api.mailchimp.com/3.0/lists/7903d14477/members/f8d090b1de0efed5b0d0da41c4763d66",
            json={"email_address": "charlie@exemple.com"},
            status=200
        )

        responses.add(
            responses.POST,
            "https://us7.api.mailchimp.com/3.0/lists/7903d14477/members/f8d090b1de0efed5b0d0da41c4763d66/tags",
            json={"tags": [{"name": "Client", "status": "active"}]},
            status=200
        )
        
        # Mock de création de Bob dans Copper
        responses.add(
            responses.POST,
            "https://api.copper.com/developer_api/v1/people",
            json={"id": 999},
            status=201
        )
        
        # Vider les détails d'opération avant le test
        operation_details.clear()
        
        # Exécuter le workflow principal
        main()
        
        # Vérifications
        assert len(responses.calls) >= 4  # Appels de base + synchronisations
        
        # Vérifier que les fichiers ont été écrits
        mock_log_file.write.assert_called()
        mock_log_file.close.assert_called()
        mock_report_file.write.assert_called()
        mock_report_file.close.assert_called()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
