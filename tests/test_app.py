import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))
from app import app, db
from models import User
from config import Config

@pytest.fixture
def client():
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Ensure there's an admin user for testing
            if not User.query.filter_by(username='admin').first():
                admin = User(username='admin', is_admin=True)
                admin.set_password('zxcvbnm')  # Set a password for the admin
                db.session.add(admin)
                db.session.commit()
        yield client

@pytest.fixture
def admin_login(client):
    # Simulate admin login
    return client.post('/login', data={"username": "admin", "password": "zxcvbnm"})

### Tests for all routes ###



# 2. Test admin login functionality
def test_login(client):
    rv = client.post('/login', data={"username": "admin", "password": "zxcvbnm"})
    assert rv.status_code == 302  # Check if redirect occurs (admin login success)
    assert rv.headers['Location'] == '/admin'  # Ensure admin is redirected to admin page

# 3. Test admin access required route (without login)
def test_admin_access_without_login(client):
    rv = client.get('/admin')
    assert rv.status_code == 302  # Should redirect to login if not authenticated
    assert rv.headers['Location'] == '/login'  # Ensure it redirects to the login page

# 4. Test registering a candidate (admin only)
def test_register_candidate(client, admin_login):
    # Simulate logged-in admin and try to register a candidate
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['is_admin'] = True

    rv = client.post('/register_candidate', json={"name": "Candidate 1"})
    assert rv.status_code == 200
    assert b"Candidate registered successfully" in rv.data

# 5. Test voting before start (should fail)
def test_vote_before_start(client):
    rv = client.post('/vote', json={"candidateId": 1, "voterAddress": "0x8FBC2d99F4b0A6bb94f63895aE192642eb7B0C41"})
    assert rv.status_code == 400  # Should return error if voting not started
    assert b"Voting is not currently active" in rv.data

# 6. Test start voting (admin only)
def test_start_voting(client, admin_login):
    # Simulate admin login and start voting
    rv = client.post('/start_voting')
    assert rv.status_code == 200
    assert b"Voting started successfully" in rv.data

# 7. Test voting after start (should succeed)
def test_vote_after_start(client, admin_login):
    # Start voting first
    client.post('/start_voting')

    # Then vote
    rv = client.post('/vote', json={"candidateId": 1, "voterAddress": "0x8FBC2d99F4b0A6bb94f63895aE192642eb7B0C41"})
    assert rv.status_code == 200
    assert b"Vote cast successfully" in rv.data

# 8. Test double voting
def test_double_vote(client, admin_login):
    client.post('/start_voting')

    # Cast the first vote
    client.post('/vote', json={"candidateId": 1, "voterAddress": "0x8FBC2d99F4b0A6bb94f63895aE192642eb7B0C41"})

    # Try voting again (should fail)
    rv = client.post('/vote', json={"candidateId": 1, "voterAddress": "0x8FBC2d99F4b0A6bb94f63895aE192642eb7B0C41"})
    assert rv.status_code == 400
    assert b"You have already voted" in rv.data

# 9. Test stop voting (admin only)
def test_stop_voting(client, admin_login):
    # Ensure voting has been started
    client.post('/start_voting')

    # Then stop voting
    rv = client.post('/stop_voting')
    assert rv.status_code == 200
    assert b"Voting stopped successfully" in rv.data

# 10. Test voting after stop (should fail)
def test_vote_after_stop(client, admin_login):
    # Ensure voting has been stopped
    client.post('/start_voting')
    client.post('/stop_voting')

    # Try to vote (should fail)
    rv = client.post('/vote', json={"candidateId": 1, "voterAddress": "0x8FBC2d99F4b0A6bb94f63895aE192642eb7B0C41"})
    assert rv.status_code == 400
    assert b"Voting is not currently active" in rv.data

# 11. Test get candidates route
def test_get_candidates(client):
    rv = client.get('/candidate_count')
    assert rv.status_code == 200
    assert b"candidateCount" in rv.data

# 12. Test admin logout
def test_logout(client, admin_login):
    rv = client.get('/logout')
    assert rv.status_code == 302  # Check if redirected after logout
    assert rv.headers['Location'] == '/login'  # Ensure redirect to login page
