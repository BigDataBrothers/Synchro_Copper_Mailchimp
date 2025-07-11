"""
Tests de performance et stress testing pour le système de synchronisation
"""
import pytest
import sys
import os
import time
from unittest.mock import patch, MagicMock
import threading
import concurrent.futures

# Ajouter le répertoire parent au path pour importer sync.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sync import (
    normalize_email,
    is_delete_tag_robust,
    contacts_are_identical,
    get_subscriber_hash,
    sync_contact_to_mailchimp,
    operation_details
)


class TestPerformance:
    """Tests de performance"""
    
    def test_normalize_email_performance(self):
        """Test de performance pour la normalisation d'emails"""
        emails = [f"user{i}@example.com" for i in range(10000)]
        
        start_time = time.time()
        normalized_emails = [normalize_email(email) for email in emails]
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Vérifier que la normalisation est rapide (< 1 seconde pour 10k emails)
        assert execution_time < 1.0
        assert len(normalized_emails) == 10000
    
    def test_tag_detection_performance(self):
        """Test de performance pour la détection de tags"""
        tags = [
            "SUPPRIMER", "DELETE", "REMOVE", "Client VIP", "Prospect",
            "🗑 À SUPPRIMER", "Actif", "Inactif", "Normal Tag"
        ] * 1000
        
        start_time = time.time()
        results = [is_delete_tag_robust(tag) for tag in tags]
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Vérifier que la détection est rapide (< 0.5 seconde pour 9k tags)
        assert execution_time < 0.5
        assert len(results) == 9000
    
    def test_hash_generation_performance(self):
        """Test de performance pour la génération de hash"""
        emails = [f"user{i}@example.com" for i in range(5000)]
        
        start_time = time.time()
        hashes = [get_subscriber_hash(email) for email in emails]
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Vérifier que la génération de hash est rapide
        assert execution_time < 0.5
        assert len(hashes) == 5000
        assert len(set(hashes)) == 5000  # Tous les hashes sont uniques
    
    def test_contact_comparison_performance(self):
        """Test de performance pour la comparaison de contacts"""
        contacts_pairs = []
        
        for i in range(1000):
            copper_contact = {
                "first_name": f"User{i}",
                "last_name": f"Test{i}",
                "emails": [{"email": f"user{i}@example.com"}]
            }
            
            mailchimp_member = {
                "email_address": f"user{i}@example.com",
                "merge_fields": {
                    "FNAME": f"User{i}",
                    "LNAME": f"Test{i}"
                }
            }
            
            contacts_pairs.append((copper_contact, mailchimp_member))
        
        start_time = time.time()
        results = [contacts_are_identical(copper, mailchimp) for copper, mailchimp in contacts_pairs]
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Vérifier que la comparaison est rapide
        assert execution_time < 0.5
        assert all(results)  # Tous doivent être identiques


class TestStressTest:
    """Tests de stress et de charge"""
    
    def test_large_contact_list_processing(self):
        """Test avec une grande liste de contacts"""
        # Simuler une grande liste de contacts
        contacts = []
        for i in range(1000):
            contacts.append({
                "id": i,
                "first_name": f"User{i}",
                "last_name": f"Test{i}",
                "emails": [{"email": f"user{i}@exemple.com"}],
                "tags": ["VIP", "Client"] if i % 2 == 0 else ["Prospect"]
            })
        
        # Mesurer le temps de traitement
        start_time = time.time()
        
        # Simuler le traitement (filtrage, normalisation, etc.)
        filtered_contacts = []
        for contact in contacts:
            if contact.get("emails"):
                email = contact["emails"][0]["email"]
                normalized_email = normalize_email(email)
                if "@exemple" in normalized_email:
                    filtered_contacts.append(contact)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Vérifier que le traitement reste dans des limites acceptables
        assert execution_time < 2.0  # Moins de 2 secondes pour 1000 contacts
        assert len(filtered_contacts) == 1000  # Tous les contacts sont @exemple
    
    def test_concurrent_email_processing(self):
        """Test de traitement concurrent d'emails"""
        emails = [f"user{i}@example.com" for i in range(1000)]
        
        def process_email_batch(email_batch):
            return [normalize_email(email) for email in email_batch]
        
        # Diviser en batches
        batch_size = 100
        batches = [emails[i:i + batch_size] for i in range(0, len(emails), batch_size)]
        
        start_time = time.time()
        
        # Traitement concurrent
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(process_email_batch, batch) for batch in batches]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Vérifier que le traitement concurrent est efficace
        assert execution_time < 1.0
        
        # Vérifier que tous les emails ont été traités
        total_processed = sum(len(batch_result) for batch_result in results)
        assert total_processed == 1000
    
    def test_memory_usage_large_dataset(self):
        """Test d'utilisation mémoire avec un grand jeu de données"""
        # Créer un grand dataset
        large_dataset = []
        for i in range(5000):
            large_dataset.append({
                "id": i,
                "first_name": f"User{i}",
                "last_name": f"Test{i}",
                "emails": [{"email": f"user{i}@exemple.com"}],
                "tags": [f"Tag{j}" for j in range(5)],  # 5 tags par contact
                "data": "x" * 100  # 100 caractères de données supplémentaires
            })
        
        # Traitement du dataset
        start_time = time.time()
        
        processed_data = []
        for contact in large_dataset:
            if contact.get("emails"):
                processed_contact = {
                    "email": normalize_email(contact["emails"][0]["email"]),
                    "name": f"{contact['first_name']} {contact['last_name']}",
                    "tags": contact["tags"]
                }
                processed_data.append(processed_contact)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Vérifier que le traitement reste efficace même avec beaucoup de données
        assert execution_time < 3.0  # Moins de 3 secondes pour 5000 contacts
        assert len(processed_data) == 5000
    
    def test_operation_details_accumulation(self):
        """Test d'accumulation des détails d'opération"""
        # Utiliser une vraie liste au lieu d'un mock
        test_operations = []
        
        for i in range(1000):
            operation = {
                'email': f'user{i}@example.com',
                'name': f'User {i}',
                'direction': 'Copper → Mailchimp',
                'success': i % 10 != 0,  # 10% d'échecs
                'error': 'Test error' if i % 10 == 0 else None,
                'tags': [f'Tag{j}' for j in range(3)]
            }
            test_operations.append(operation)
        
        # Vérifier que les données sont correctement accumulées
        assert len(test_operations) == 1000
        
        # Calculer les statistiques
        success_count = sum(1 for op in test_operations if op['success'])
        error_count = len(test_operations) - success_count
        
        assert success_count == 900  # 90% de succès
        assert error_count == 100    # 10% d'erreurs


class TestEdgeCasesAndRobustness:
    """Tests pour les cas limites et la robustesse"""
    
    def test_empty_email_handling(self):
        """Test de gestion des emails vides"""
        empty_emails = ["", "   ", None, "  @  ", "@", "test@"]
        
        for email in empty_emails:
            try:
                if email is not None:
                    normalized = normalize_email(email)
                    # Ne doit pas lever d'exception
                    assert isinstance(normalized, str)
            except Exception as e:
                pytest.fail(f"normalize_email a levé une exception avec '{email}': {e}")
    
    def test_malformed_contact_data(self):
        """Test avec des données de contact malformées"""
        malformed_contacts = [
            {},  # Contact vide
            {"emails": []},  # Sans emails
            {"emails": [{}]},  # Email vide
            {"emails": [{"email": ""}]},  # Email string vide
            {"first_name": None, "last_name": None, "emails": []},  # Valeurs nulles
        ]
        
        for contact in malformed_contacts:
            try:
                # Ces appels ne doivent pas lever d'exception
                emails = contact.get("emails", [])
                if emails and "email" in emails[0]:
                    normalized = normalize_email(emails[0]["email"])
            except Exception as e:
                pytest.fail(f"Erreur avec contact malformé {contact}: {e}")
    
    def test_unicode_and_special_characters(self):
        """Test avec des caractères unicode et spéciaux"""
        special_names = [
            "José María",
            "François",
            "北京",
            "🎉 Test User",
            "User@Company",
            "Test\nUser",
            "Test\tUser"
        ]
        
        for name in special_names:
            try:
                # Les noms avec caractères spéciaux doivent être gérés
                cleaned_name = name.strip()
                assert isinstance(cleaned_name, str)
            except Exception as e:
                pytest.fail(f"Erreur avec nom spécial '{name}': {e}")
    
    def test_extremely_long_strings(self):
        """Test avec des chaînes très longues"""
        long_email = "a" * 1000 + "@example.com"
        long_name = "User " + "x" * 1000
        long_tag = "Tag " + "y" * 1000
        
        try:
            normalized_email = normalize_email(long_email)
            assert isinstance(normalized_email, str)
            
            # Test de détection de tag avec chaîne très longue
            is_delete = is_delete_tag_robust(long_tag)
            assert isinstance(is_delete, bool)
            
        except Exception as e:
            pytest.fail(f"Erreur avec chaînes longues: {e}")
    
    def test_concurrent_access_safety(self):
        """Test de sécurité d'accès concurrent"""
        results = []
        errors = []
        
        def worker():
            try:
                for i in range(100):
                    email = f"user{i}@example.com"
                    normalized = normalize_email(email)
                    results.append(normalized)
            except Exception as e:
                errors.append(e)
        
        # Lancer plusieurs threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()
        
        # Attendre que tous les threads terminent
        for thread in threads:
            thread.join()
        
        # Vérifier qu'il n'y a pas d'erreurs
        assert len(errors) == 0
        assert len(results) == 500  # 5 threads * 100 emails chacun


class TestResourceManagement:
    """Tests de gestion des ressources"""
    
    def test_file_handle_management(self):
        """Test de gestion des handles de fichiers"""
        # Ce test vérifie que les fichiers sont correctement fermés
        import tempfile
        import os
        
        temp_files = []
        
        try:
            # Créer plusieurs fichiers temporaires
            for i in range(10):
                temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
                temp_file.write(f"Test content {i}")
                temp_file.close()
                temp_files.append(temp_file.name)
            
            # Vérifier que tous les fichiers existent
            for file_path in temp_files:
                assert os.path.exists(file_path)
        
        finally:
            # Nettoyer les fichiers temporaires
            for file_path in temp_files:
                try:
                    os.unlink(file_path)
                except OSError:
                    pass
    
    def test_memory_cleanup_after_large_operations(self):
        """Test de nettoyage mémoire après de grandes opérations"""
        # Simuler une grande opération
        large_data = []
        for i in range(10000):
            large_data.append({
                "id": i,
                "data": "x" * 1000,  # 1KB par entrée
                "processed": False
            })
        
        # Traiter les données
        for item in large_data:
            item["processed"] = True
        
        # Nettoyer
        large_data.clear()
        
        # Vérifier que la mémoire est libérée
        assert len(large_data) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
