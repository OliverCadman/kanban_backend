"""Unit Tests for App Configuration"""

from application import create_app
import flask_unittest
import json
from unittest.mock import patch
from application.database import mongo

from werkzeug.security import check_password_hash


def client_post_helper(client, endpoint, data):
    return client.post(endpoint, data=json.dumps(data), content_type='application/json')


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
    
    # def test_user_register_invalid_email_error(self, client):
    #     """Test error thrown if email is invalid"""

    #     payload = {
    #         "username": "Test User",
    #         "email": "test",
    #         "password": "TestPass123!"
    #     }

    #     res = client.post(
    #         "/register", data=json.dumps(payload), 
    #         content_type="application/json")

    #     self.assertEqual(res.status_code, 400)
    #     self.assertEqual(res.data, b"Email is invalid.")
    
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

    def test_verify_token(self, client):
        """
        Test token generation and verification methods function correctly,
        and update the associated user object's 'is_confirmed' field to True.
        """
        payload = {
            "username": "Test User",
            "email": "gimar23687@glumark.com",
            "password": "Testpass123!"
        }
        
        res = client.post("/register", data=json.dumps(payload), content_type="application/json")
        data = json.loads(res.data)
        email = data['email']
        self.assertEqual(email, payload['email'])

        res = client.get(f"/confirm_email/{data['token']}")

        user = mongo.db.users.find_one({'email': payload['email']})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(user['email'], payload['email'])
        self.assertTrue(check_password_hash(user['password'], payload['password']))
        self.assertTrue(user['is_confirmed'])
    
    def test_verify_token_error(self, client):
        """Test 400 error thrown if attempt to verify email with incorrect token."""

        payload = {
            "username": "Test User",
            "email": "test8@email.com",
            "password": "testPass123!"
        }

        res = client.post('/register', data=json.dumps(payload), content_type='application/json')

        res = client.get("/confirm_email/incorrect_token")
        self.assertEqual(res.status_code, 400)
        self.assertEqual(json.loads(res.data)['msg'], 'The link is either invalid or has expired.')

        user = mongo.db.users.find_one({'email': payload['email']})
        self.assertFalse(user['is_confirmed'] == True)
    
    def test_get_jwt_token(self, client):
        """Test authenticating registered user and return of JWT"""

        payload = {
            "username": "Test User",
            "email": "test9@email.com",
            "password": "testPass123!"
        }

        res = client_post_helper(client, '/register', payload)
        self.assertEqual(res.status_code, 201)
        res = client_post_helper(client, '/login', {
            "email": payload["email"],
            "password": payload["password"]
        })

        self.assertEqual(res.status_code, 200)
        self.assertIn("token", json.loads(res.data))
    
    def test_get_jwt_token_error(self, client):
        """Test error raised if logging in with bad password."""

        payload = {
            "username": "Test User",
            "email": "test10@email.com",
            "password": "testPass123!"
        }

        res = client_post_helper(client, "/register", payload)

        res = client_post_helper(client, "login", {
            "email": "test10@email.com",
            "password": "badPassword123!"
        })

        self.assertEqual(res.status_code, 401)
        self.assertEqual(json.loads(res.data)['msg'], 'Your password is invalid.')

    def tearDown(self, client):
        # Clear dev database after running tests
        self.mongo.db.users.delete_many({})
