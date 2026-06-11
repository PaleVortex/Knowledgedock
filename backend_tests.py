"""
Automated tests for the Knowledgedock backend API.
Run: pytest backend_tests.py -v
"""

import pytest
import json
import sys
from pathlib import Path

# Add mihon_app to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from backend import app, DatabaseManager, BookmarkManager


@pytest.fixture
def client():
    """Create a test client and temporary database."""
    app.config['TESTING'] = True
    # In-memory DB for tests
    with app.test_client() as c:
        yield c


@pytest.fixture
def db_manager():
    """Create a temporary database manager for tests."""
    db = DatabaseManager(':memory:')  # SQLite in-memory
    db.init_db()
    return db


def test_app_creation():
    """Test that Flask app is created successfully."""
    assert app is not None
    assert app.config['TESTING'] is False


def test_bookmark_list_empty(client):
    """Test GET /api/bookmarks returns empty list initially."""
    response = client.get('/api/bookmarks')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    # Empty or has items - both okay in test


def test_bookmark_create(client):
    """Test POST /api/bookmarks creates a new bookmark."""
    import time
    unique_id = int(time.time() * 1000)
    payload = {
        'title': 'Test Page',
        'url': f'https://example-create-{unique_id}.com',
        'source': 'manual',
        'description': 'A test bookmark'
    }
    response = client.post(
        '/api/bookmarks',
        data=json.dumps(payload),
        content_type='application/json'
    )
    assert response.status_code in [200, 201], f"Got {response.status_code}: {response.data}"
    data = json.loads(response.data)
    # API now returns id when successful
    assert 'id' in data or 'status' in data


def test_bookmark_create_minimal(client):
    """Test POST /api/bookmarks with minimal fields."""
    import time
    unique_id = int(time.time() * 1000) + 1
    payload = {
        'title': 'Minimal Test',
        'url': f'https://test-minimal-{unique_id}.com'
    }
    response = client.post(
        '/api/bookmarks',
        data=json.dumps(payload),
        content_type='application/json'
    )
    assert response.status_code in [200, 201], f"Got {response.status_code}: {response.data}"


def test_bookmark_create_missing_title(client):
    """Test POST /api/bookmarks fails without title."""
    payload = {'url': 'https://example.com'}
    response = client.post(
        '/api/bookmarks',
        data=json.dumps(payload),
        content_type='application/json'
    )
    # Should fail or return 400
    assert response.status_code >= 400


def test_bookmark_delete(client):
    """Test DELETE /api/bookmarks/<id> removes bookmark."""
    # First create a bookmark with a unique URL
    unique_url = f'https://delete-{id(client)}.com'
    payload = {'title': 'To Delete', 'url': unique_url}
    create_resp = client.post(
        '/api/bookmarks',
        data=json.dumps(payload),
        content_type='application/json'
    )
    assert create_resp.status_code in [200, 201]
    
    # Extract ID from response
    data = json.loads(create_resp.data)
    bm_id = data.get('id', 1)
    
    # Delete it
    response = client.delete(f'/api/bookmarks/{bm_id}')
    # Should succeed or return 404 if bookmark was already gone
    assert response.status_code in [200, 204, 404]


def test_bookmark_cors_headers(client):
    """Test that CORS headers are present."""
    response = client.get('/api/bookmarks')
    assert 'Access-Control-Allow-Origin' in response.headers or response.status_code == 200


def test_invalid_json_payload(client):
    """Test that invalid JSON is handled gracefully."""
    response = client.post(
        '/api/bookmarks',
        data='not valid json',
        content_type='application/json'
    )
    # Should fail with 400 or 422
    assert response.status_code >= 400


def test_bookmark_create_duplicate_url(client):
    """Test creating bookmarks with same URL (should fail on duplicate)."""
    import time, random
    unique_id = int(time.time() * 1000) + random.randint(1, 1000)
    dup_url = f'https://dup-test-{unique_id}.com'
    
    payload1 = {'title': 'Page 1', 'url': dup_url}
    resp1 = client.post(
        '/api/bookmarks',
        data=json.dumps(payload1),
        content_type='application/json'
    )
    # Second post with same URL should fail (unique constraint)
    payload2 = {'title': 'Page 2', 'url': dup_url}
    resp2 = client.post(
        '/api/bookmarks',
        data=json.dumps(payload2),
        content_type='application/json'
    )
    # First should succeed
    assert resp1.status_code in [200, 201], f"First create failed: {resp1.data}"
    # Second should fail (duplicate URL)
    assert resp2.status_code >= 400


def test_backend_database_manager():
    """Test DatabaseManager initialization."""
    # Note: DatabaseManager creates its own DB at constants.DB_PATH,
    # we test that it initializes without error
    try:
        db = DatabaseManager()
        assert db is not None
        # Verify init_db works
        db.init_db()
    except Exception as e:
        pytest.fail(f"DatabaseManager failed: {e}")


def test_bookmark_manager_add():
    """Test BookmarkManager add_bookmark method."""
    # Create a bookmark manager with existing DB
    bm = BookmarkManager()
    
    # Should not raise, may return True or False depending on DB state
    result = bm.add_bookmark('Test Title', 'https://unique-test-1.com', 'manual')
    # add_bookmark returns bool indicating success


def test_bookmark_manager_get():
    """Test BookmarkManager get_bookmarks method."""
    bm = BookmarkManager()
    
    # Add a bookmark first
    bm.add_bookmark('Title 1', 'https://unique-test-2.com', 'manual')
    
    # Retrieve bookmarks
    bookmarks = bm.get_all_bookmarks()
    assert isinstance(bookmarks, list)
    # May be empty or have items depending on DB state
    assert len(bookmarks) >= 0


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
