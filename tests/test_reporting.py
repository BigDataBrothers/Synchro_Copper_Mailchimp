"""
Tests unitaires pour les fonctions de rapport et de logging
"""
import pytest
import sys
import os
from unittest.mock import patch, MagicMock, mock_open, call
import json
from datetime import datetime
import io

# Ajouter le répertoire parent au path pour importer sync.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sync import (
    log,
    write_import_report,
    handle_marked_contacts,
    Colors,
    operation_details
)


class TestLogging:
    """Tests pour le système de logging"""
    
    @patch('builtins.print')
    @patch('sync.log_file')
    def test_log_info_message(self, mock_log_file, mock_print):
        """Test d'un message de log INFO"""
        mock_log_file.write = MagicMock()
        mock_log_file.flush = MagicMock()
        
        log("Test message", "INFO")
        
        # Vérifier que print a été appelé
        mock_print.assert_called_once()
        
        # Vérifier le contenu du message console
        console_message = mock_print.call_args[0][0]
        assert "Test message" in console_message
        assert Colors.BLUE in console_message
        assert "ℹ️" in console_message
        
        # Vérifier l'écriture dans le fichier
        mock_log_file.write.assert_called_once()
        mock_log_file.flush.assert_called_once()
    
    @patch('builtins.print')
    @patch('sync.log_file')
    def test_log_error_message(self, mock_log_file, mock_print):
        """Test d'un message de log ERROR"""
        mock_log_file.write = MagicMock()
        mock_log_file.flush = MagicMock()
        
        log("Error occurred", "ERROR")
        
        # Vérifier que print a été appelé
        mock_print.assert_called_once()
        
        # Vérifier le contenu du message console
        console_message = mock_print.call_args[0][0]
        assert "Error occurred" in console_message
        assert Colors.RED in console_message
        assert "❌" in console_message
    
    @patch('builtins.print')
    @patch('sync.log_file')
    def test_log_success_message(self, mock_log_file, mock_print):
        """Test d'un message de log SUCCESS"""
        mock_log_file.write = MagicMock()
        mock_log_file.flush = MagicMock()
        
        log("Operation successful", "SUCCESS")
        
        # Vérifier que print a été appelé
        mock_print.assert_called_once()
        
        # Vérifier le contenu du message console
        console_message = mock_print.call_args[0][0]
        assert "Operation successful" in console_message
        assert Colors.GREEN in console_message
        assert "✅" in console_message
    
    @patch('builtins.print')
    @patch('sync.log_file')
    def test_log_warning_message(self, mock_log_file, mock_print):
        """Test d'un message de log WARNING"""
        mock_log_file.write = MagicMock()
        mock_log_file.flush = MagicMock()
        
        log("Warning message", "WARNING")
        
        # Vérifier que print a été appelé
        mock_print.assert_called_once()
        
        # Vérifier le contenu du message console
        console_message = mock_print.call_args[0][0]
        assert "Warning message" in console_message
        assert Colors.YELLOW in console_message
        assert "⚠️" in console_message


class TestReporting:
    """Tests pour le système de rapport"""
    
    @patch('sync.report_file')
    @patch('sync.TEST_MODE', True)
    def test_write_import_report_success(self, mock_report_file):
        """Test de génération de rapport avec succès"""
        mock_report_file.write = MagicMock()
        mock_report_file.flush = MagicMock()
        mock_report_file.close = MagicMock()
        
        # Données de test
        report_data = {
            'operations': [
                {
                    'email': 'test@exemple.com',
                    'name': 'Test User',
                    'direction': 'Copper → Mailchimp',
                    'success': True,
                    'tags': ['VIP', 'Client']
                }
            ],
            'copper_to_mc': 1,
            'mc_to_copper': 0,
            'identical_contacts': 0,
            'excluded': 0,
            'marked_for_deletion': 0,
            'marked_contacts': []
        }
        
        result = write_import_report(report_data)
        
        # Vérifier que les méthodes ont été appelées
        mock_report_file.write.assert_called_once()
        mock_report_file.flush.assert_called_once()
        mock_report_file.close.assert_called_once()
        
        # Vérifier le contenu du rapport
        report_content = mock_report_file.write.call_args[0][0]
        assert "RAPPORT D'IMPORTATION" in report_content
        assert "TEST (@exemple uniquement)" in report_content
        assert "test@exemple.com" in report_content
        assert "Copper → Mailchimp" in report_content
        assert "✅ SUCCÈS" in report_content
        assert "VIP, Client" in report_content
    
    @patch('sync.report_file')
    @patch('sync.TEST_MODE', False)
    def test_write_import_report_production_mode(self, mock_report_file):
        """Test de génération de rapport en mode production"""
        mock_report_file.write = MagicMock()
        mock_report_file.flush = MagicMock()
        mock_report_file.close = MagicMock()
        
        report_data = {
            'operations': [],
            'copper_to_mc': 0,
            'mc_to_copper': 0,
            'identical_contacts': 0,
            'excluded': 0,
            'marked_for_deletion': 0,
            'marked_contacts': []
        }
        
        result = write_import_report(report_data)
        
        # Vérifier le mode production
        report_content = mock_report_file.write.call_args[0][0]
        assert "PRODUCTION (toute la base)" in report_content
    
    @patch('sync.report_file')
    @patch('sync.TEST_MODE', True)
    def test_write_import_report_with_errors(self, mock_report_file):
        """Test de génération de rapport avec erreurs"""
        mock_report_file.write = MagicMock()
        mock_report_file.flush = MagicMock()
        mock_report_file.close = MagicMock()
        
        report_data = {
            'operations': [
                {
                    'email': 'error@exemple.com',
                    'name': 'Error User',
                    'direction': 'Copper → Mailchimp',
                    'success': False,
                    'error': 'API Error 500',
                    'tags': []
                }
            ],
            'copper_to_mc': 0,
            'mc_to_copper': 0,
            'identical_contacts': 0,
            'excluded': 0,
            'marked_for_deletion': 0,
            'marked_contacts': []
        }
        
        result = write_import_report(report_data)
        
        # Vérifier le contenu du rapport
        report_content = mock_report_file.write.call_args[0][0]
        assert "❌ ERREUR" in report_content
        assert "error@exemple.com" in report_content
        assert "API Error 500" in report_content
    
    @patch('sync.report_file')
    @patch('sync.TEST_MODE', True)
    def test_write_import_report_with_marked_contacts(self, mock_report_file):
        """Test de génération de rapport avec contacts marqués"""
        mock_report_file.write = MagicMock()
        mock_report_file.flush = MagicMock()
        mock_report_file.close = MagicMock()
        
        report_data = {
            'operations': [],
            'copper_to_mc': 0,
            'mc_to_copper': 0,
            'identical_contacts': 0,
            'excluded': 0,
            'marked_for_deletion': 1,
            'marked_contacts': [
                {
                    'email': 'marked@exemple.com',
                    'name': 'Marked User',
                    'detected_tag': '🗑 À SUPPRIMER'
                }
            ]
        }
        
        result = write_import_report(report_data)
        
        # Vérifier le contenu du rapport
        report_content = mock_report_file.write.call_args[0][0]
        assert "CONTACTS MARQUÉS POUR SUPPRESSION" in report_content
        assert "marked@exemple.com" in report_content
        assert "🗑 À SUPPRIMER" in report_content
    
    @patch('sync.report_file')
    @patch('sync.TEST_MODE', True)
    def test_write_import_report_no_operations(self, mock_report_file):
        """Test de génération de rapport sans opérations"""
        mock_report_file.write = MagicMock()
        mock_report_file.flush = MagicMock()
        mock_report_file.close = MagicMock()
        
        report_data = {
            'operations': [],
            'copper_to_mc': 0,
            'mc_to_copper': 0,
            'identical_contacts': 0,
            'excluded': 0,
            'marked_for_deletion': 0,
            'marked_contacts': []
        }
        
        result = write_import_report(report_data)
        
        # Vérifier le contenu du rapport
        report_content = mock_report_file.write.call_args[0][0]
        assert "Aucune opération de synchronisation effectuée" in report_content
        assert "Aucune synchronisation nécessaire" in report_content


class TestContactHandling:
    """Tests pour la gestion des contacts marqués"""
    
    @patch('builtins.input', side_effect=['i'])
    @patch('sync.log')
    def test_handle_marked_contacts_ignore(self, mock_log, mock_input):
        """Test d'ignorage des contacts marqués"""
        marked_contacts = [
            {
                'email': 'test@exemple.com',
                'name': 'Test User',
                'detected_tag': '🗑 À SUPPRIMER'
            }
        ]
        
        handle_marked_contacts(marked_contacts)
        
        # Vérifier que le log d'ignorage a été appelé
        mock_log.assert_called_with("ℹ️ Contacts ignorés pour cette session", "INFO")
    
    @patch('builtins.input', side_effect=['g', 'a'])
    @patch('sync.archive_contact')
    @patch('sync.log')
    def test_handle_marked_contacts_archive_group(self, mock_log, mock_archive, mock_input):
        """Test d'archivage en groupe des contacts marqués"""
        marked_contacts = [
            {
                'email': 'test1@exemple.com',
                'name': 'Test User 1',
                'detected_tag': '🗑 À SUPPRIMER'
            },
            {
                'email': 'test2@exemple.com',
                'name': 'Test User 2',
                'detected_tag': '🗑 À SUPPRIMER'
            }
        ]
        
        handle_marked_contacts(marked_contacts)
        
        # Vérifier que archive_contact a été appelé pour chaque contact
        assert mock_archive.call_count == 2
        mock_archive.assert_any_call(marked_contacts[0])
        mock_archive.assert_any_call(marked_contacts[1])
    
    @patch('builtins.input', side_effect=['g', 's'])
    @patch('sync.delete_contact')
    @patch('sync.log')
    def test_handle_marked_contacts_delete_group(self, mock_log, mock_delete, mock_input):
        """Test de suppression en groupe des contacts marqués"""
        marked_contacts = [
            {
                'email': 'test@exemple.com',
                'name': 'Test User',
                'detected_tag': '🗑 À SUPPRIMER'
            }
        ]
        
        handle_marked_contacts(marked_contacts)
        
        # Vérifier que delete_contact a été appelé
        mock_delete.assert_called_once_with(marked_contacts[0])
    
    @patch('builtins.input', side_effect=['t', 'a'])
    @patch('sync.archive_contact')
    @patch('sync.log')
    @patch('builtins.print')
    def test_handle_marked_contacts_individual_archive(self, mock_print, mock_log, mock_archive, mock_input):
        """Test d'archivage individuel des contacts marqués"""
        marked_contacts = [
            {
                'email': 'test@exemple.com',
                'name': 'Test User',
                'detected_tag': '🗑 À SUPPRIMER'
            }
        ]
        
        handle_marked_contacts(marked_contacts)
        
        # Vérifier que archive_contact a été appelé
        mock_archive.assert_called_once_with(marked_contacts[0])
    
    @patch('builtins.input', side_effect=['t', 's'])
    @patch('sync.delete_contact')
    @patch('sync.log')
    @patch('builtins.print')
    def test_handle_marked_contacts_individual_delete(self, mock_print, mock_log, mock_delete, mock_input):
        """Test de suppression individuelle des contacts marqués"""
        marked_contacts = [
            {
                'email': 'test@exemple.com',
                'name': 'Test User',
                'detected_tag': '🗑 À SUPPRIMER'
            }
        ]
        
        handle_marked_contacts(marked_contacts)
        
        # Vérifier que delete_contact a été appelé
        mock_delete.assert_called_once_with(marked_contacts[0])
    
    @patch('builtins.input', side_effect=['t', 'i'])
    @patch('sync.archive_contact')
    @patch('sync.delete_contact')
    @patch('sync.log')
    @patch('builtins.print')
    def test_handle_marked_contacts_individual_ignore(self, mock_print, mock_log, mock_delete, mock_archive, mock_input):
        """Test d'ignorage individuel des contacts marqués"""
        marked_contacts = [
            {
                'email': 'test@exemple.com',
                'name': 'Test User',
                'detected_tag': '🗑 À SUPPRIMER'
            }
        ]
        
        handle_marked_contacts(marked_contacts)
        
        # Vérifier qu'aucune action n'a été prise
        mock_archive.assert_not_called()
        mock_delete.assert_not_called()
    
    @patch('sync.log')
    def test_handle_marked_contacts_empty_list(self, mock_log):
        """Test avec une liste vide de contacts marqués"""
        marked_contacts = []
        
        handle_marked_contacts(marked_contacts)
        
        # Vérifier que le log approprié a été appelé
        mock_log.assert_called_with("✅ Aucun contact marqué pour suppression", "SUCCESS")


class TestStatisticsAndReporting:
    """Tests pour les statistiques et rapports"""
    
    def test_report_statistics_calculation(self):
        """Test du calcul des statistiques de rapport"""
        # Données de test
        operations = [
            {'success': True},
            {'success': True},
            {'success': False},
            {'success': True}
        ]
        
        total = len(operations)
        success_count = sum(1 for op in operations if op['success'])
        error_count = total - success_count
        success_rate = (success_count / total * 100) if total > 0 else 0
        
        assert total == 4
        assert success_count == 3
        assert error_count == 1
        assert success_rate == 75.0
    
    def test_report_statistics_no_operations(self):
        """Test du calcul des statistiques sans opérations"""
        operations = []
        
        total = len(operations)
        success_count = sum(1 for op in operations if op['success'])
        error_count = total - success_count
        success_rate = (success_count / total * 100) if total > 0 else 0
        
        assert total == 0
        assert success_count == 0
        assert error_count == 0
        assert success_rate == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
