from application import create_app
from application.test_helpers import client_post_helper
from application.database import mongo
import flask_unittest

import json


class BoardAPITests(flask_unittest.ClientTestCase):
    """Unit tests for the Board API"""

    app = create_app()

    def setUp(self, client):

        payload = {
            "username": "Test User",
            "email": "test13@email.com",
            "password": "testPass123!"
        }

        self.user = client_post_helper(client, '/register', payload)

    
    def test_board_create(self, client):
        print('TESTING BOARD CREATE...')
    
    def tearDown(self, client):
        mongo.db.users.delete_many({})
