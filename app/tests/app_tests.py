"""Unit Tests for App Configuration"""

from application import create_app
import flask_unittest
import json


class TestAppRunning(flask_unittest.ClientTestCase):

    app = create_app()


    def test_user_profile_get(self, client):
        res = client.get('/user_profile')

        self.assertIn(b'User Profile', res.data)
        self.assertEqual(res.status_code, 200)
    
    def test_register(self, client):
        payload = {
            "username": "Test User",
            "email": "test@example.com",
            "password": "testpass123"
        }

        res = client.post(
            '/register', data=json.dumps(payload), 
            content_type="application/json")

        print('RESPONSE:', res.data)
        self.assertEqual(res.status_code, 201)
