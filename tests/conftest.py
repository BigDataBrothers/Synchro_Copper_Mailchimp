"""
Configuration pour les tests pytest
"""
import pytest
import sys
import os
from unittest.mock import MagicMock, patch

# Ajouter le répertoire parent au path pour importer sync.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuration des fixtures globales
@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Configuration de l'environnement de test"""
    # Mock des variables d'environnement
    test_env = {
        "COPPER_API_URL": "https://api.copper.com/developer_api/v1",
        "COPPER_API_EMAIL": "test@example.com",
        "COPPER_API_KEY": "test_copper_key",
        "MAILCHIMP_API_KEY": "test_mailchimp_key",
        "MAILCHIMP_DC": "us1",
        "MAILCHIMP_LIST_ID": "test_list_id"
    }
    
    with patch.dict(os.environ, test_env):
        yield


@pytest.fixture(autouse=True)
def mock_file_operations():
    """Mock des opérations de fichiers pour éviter la création de fichiers réels"""
    with patch('sync.log_file') as mock_log_file, \
         patch('sync.report_file') as mock_report_file:
        
        # Configurer les mocks
        mock_log_file.write = MagicMock()
        mock_log_file.flush = MagicMock()
        mock_log_file.close = MagicMock()
        
        mock_report_file.write = MagicMock()
        mock_report_file.flush = MagicMock()
        mock_report_file.close = MagicMock()
        
        yield


@pytest.fixture
def sample_copper_contact():
    """Fixture pour un contact Copper de test"""
    return {
        "id": 123,
        "first_name": "John",
        "last_name": "Doe",
        "emails": [{"email": "john.doe@exemple.com"}],
        "tags": ["VIP", "Client"]
    }


@pytest.fixture
def sample_mailchimp_member():
    """Fixture pour un membre Mailchimp de test"""
    return {
        "email_address": "john.doe@exemple.com",
        "merge_fields": {
            "FNAME": "John",
            "LNAME": "Doe"
        },
        "status": "subscribed"
    }


@pytest.fixture
def sample_marked_contact():
    """Fixture pour un contact marqué pour suppression"""
    return {
        "id": 456,
        "first_name": "Jane",
        "last_name": "Smith",
        "emails": [{"email": "jane.smith@exemple.com"}],
        "tags": ["🗑 À SUPPRIMER", "Client"]
    }


@pytest.fixture
def sample_inactive_contact():
    """Fixture pour un contact inactif"""
    return {
        "id": 789,
        "first_name": "Bob",
        "last_name": "Johnson",
        "emails": [{"email": "bob.johnson@exemple.com"}],
        "tags": ["📥 INACTIF", "Ancien client"]
    }


@pytest.fixture
def reset_operation_details():
    """Fixture pour réinitialiser les détails d'opération"""
    import sync
    original_details = sync.operation_details.copy()
    sync.operation_details.clear()
    yield
    sync.operation_details = original_details


# Configuration des markers personnalisés
def pytest_configure(config):
    """Configuration des markers personnalisés"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "api: marks tests that require API calls"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )


# Configuration des options de ligne de commande
def pytest_addoption(parser):
    """Ajout d'options de ligne de commande personnalisées"""
    parser.addoption(
        "--run-slow", action="store_true", default=False,
        help="run slow tests"
    )
    parser.addoption(
        "--run-integration", action="store_true", default=False,
        help="run integration tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modification de la collection de tests"""
    if config.getoption("--run-slow"):
        # Ne pas filtrer les tests lents
        return
    
    skip_slow = pytest.mark.skip(reason="need --run-slow option to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)
    
    if not config.getoption("--run-integration"):
        skip_integration = pytest.mark.skip(reason="need --run-integration option to run")
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_integration)


# Fixtures pour les tests d'API
@pytest.fixture
def mock_copper_api():
    """Mock de l'API Copper"""
    with patch('requests.post') as mock_post, \
         patch('requests.get') as mock_get, \
         patch('requests.put') as mock_put, \
         patch('requests.delete') as mock_delete:
        
        # Configuration des réponses par défaut
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_response.raise_for_status.return_value = None
        
        mock_post.return_value = mock_response
        mock_get.return_value = mock_response
        mock_put.return_value = mock_response
        mock_delete.return_value = mock_response
        
        yield {
            'post': mock_post,
            'get': mock_get,
            'put': mock_put,
            'delete': mock_delete,
            'response': mock_response
        }


@pytest.fixture
def mock_mailchimp_api():
    """Mock de l'API Mailchimp"""
    with patch('requests.get') as mock_get, \
         patch('requests.put') as mock_put, \
         patch('requests.post') as mock_post, \
         patch('requests.patch') as mock_patch, \
         patch('requests.delete') as mock_delete:
        
        # Configuration des réponses par défaut
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_response.raise_for_status.return_value = None
        
        mock_get.return_value = mock_response
        mock_put.return_value = mock_response
        mock_post.return_value = mock_response
        mock_patch.return_value = mock_response
        mock_delete.return_value = mock_response
        
        yield {
            'get': mock_get,
            'put': mock_put,
            'post': mock_post,
            'patch': mock_patch,
            'delete': mock_delete,
            'response': mock_response
        }


# Fixtures pour les données de test
@pytest.fixture
def large_contact_dataset():
    """Fixture pour un grand jeu de données de contacts"""
    contacts = []
    for i in range(1000):
        contacts.append({
            "id": i,
            "first_name": f"User{i}",
            "last_name": f"Test{i}",
            "emails": [{"email": f"user{i}@exemple.com"}],
            "tags": [f"Tag{j}" for j in range(3)]
        })
    return contacts


@pytest.fixture
def mixed_contact_dataset():
    """Fixture pour un jeu de données mixte (avec contacts normaux, marqués, inactifs)"""
    contacts = []
    
    # Contacts normaux
    for i in range(100):
        contacts.append({
            "id": i,
            "first_name": f"User{i}",
            "last_name": f"Test{i}",
            "emails": [{"email": f"user{i}@exemple.com"}],
            "tags": ["VIP", "Client"]
        })
    
    # Contacts marqués pour suppression
    for i in range(100, 110):
        contacts.append({
            "id": i,
            "first_name": f"Marked{i}",
            "last_name": f"User{i}",
            "emails": [{"email": f"marked{i}@exemple.com"}],
            "tags": ["🗑 À SUPPRIMER", "Client"]
        })
    
    # Contacts inactifs
    for i in range(110, 120):
        contacts.append({
            "id": i,
            "first_name": f"Inactive{i}",
            "last_name": f"User{i}",
            "emails": [{"email": f"inactive{i}@exemple.com"}],
            "tags": ["📥 INACTIF", "Ancien client"]
        })
    
    return contacts


# Utilitaires pour les tests
class TestUtils:
    """Classe utilitaire pour les tests"""
    
    @staticmethod
    def create_copper_contact(id_num, first_name, last_name, email, tags=None):
        """Créer un contact Copper de test"""
        return {
            "id": id_num,
            "first_name": first_name,
            "last_name": last_name,
            "emails": [{"email": email}],
            "tags": tags or []
        }
    
    @staticmethod
    def create_mailchimp_member(email, first_name, last_name, status="subscribed"):
        """Créer un membre Mailchimp de test"""
        return {
            "email_address": email,
            "merge_fields": {
                "FNAME": first_name,
                "LNAME": last_name
            },
            "status": status
        }
    
    @staticmethod
    def assert_operation_recorded(operation_details, email, direction, success=True):
        """Vérifier qu'une opération a été enregistrée"""
        matching_operations = [
            op for op in operation_details 
            if op['email'] == email and op['direction'] == direction
        ]
        assert len(matching_operations) > 0, f"Opération {direction} pour {email} non trouvée"
        if success is not None:
            assert matching_operations[0]['success'] == success


@pytest.fixture
def test_utils():
    """Fixture pour les utilitaires de test"""
    return TestUtils
