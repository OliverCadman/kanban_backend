"""Unit Tests for App Configuration"""

from application import create_app
import flask_unittest
import json

from application.database import mongo

class UserAPITests(flask_unittest.ClientTestCase):

    app = create_app()
    def setUp(self, client):
        self.mongo = mongo


    def test_user_profile_get(self, client):
        res = client.get('/user_profile')

        self.assertIn(b'User Profile', res.data)
        self.assertEqual(res.status_code, 200)
    
    def test_register(self, client):
        """Test registering a new user is successful"""
        payload = {
            "username": "Test User",
            "email": "test1@example.com",
            "password": "testPass123!"
        }

        res = client.post(
            '/register', data=json.dumps(payload), 
            content_type="application/json")

        self.assertEqual(res.status_code, 201)
 
    
    def test_register_user_email_exists_error(self, client):
        """
        Test error raised if user tries to register
        with an existing email.
        """

        payload = {
            "username": "Test User",
            "email": "test2@example.com",
            "password": "testPass123!"
        }
    
        client.post('/register', data=json.dumps(payload), content_type="application/json")

        res = client.post('/register', data=json.dumps(payload), content_type="application/json")

        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.data, b'Email already exists.')
    
    def test_password_too_short_error(self, client):
        """Test error raised if password is too short."""

        payload = {
            "username": "Test User",
            "email": "test3@email.com",
            "password": "Test"
        }

        res = client.post(
            '/register', data=json.dumps(payload), content_type="application/json")
        
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.data, b'Password is too short.')
    
    def test_password_no_uppercase_letter_error(self, client):
        """Test error raised if password does not contain capital letter."""

        payload = {
            "username": "Test User",
            "email": "test4@email.com",
            "password": "testpassword123"
        }

        res = client.post(
            '/register', data=json.dumps(payload), content_type="application/json")
        
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.data, b'Your password should contain at least one uppercase letter.')
    
    def test_password_no_digit_error(self, client):
        """Test error raised if password does not contain at least one digit."""

        payload = {
            "username": "Test User",
            "email": "test5@email.com",
            "password": "testPassword"
        }

        res = client.post(
            '/register', data=json.dumps(payload), content_type="application/json")
        
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.data, b'Your password should contain at least one number.')

    def test_password_no_special_char_error(self, client):
        """Test error raised if password does not contain at least one special character."""

        payload = {
            "username": "Test User",
            "email": "test6@email.com",
            "password": "testPassword123"
        }

        res = client.post(
            '/register', data=json.dumps(payload), content_type="application/json")
        
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.data, b'Your password should contain at least one special character.')

    def tearDown(self, client):
        # Clear dev database after running tests
        self.mongo.db.users.delete_many({})
