from application import create_app
from application.test_helpers import client_post_helper
from application.database import mongo
import flask_unittest

import json


class BoardAPITests(flask_unittest.AppClientTestCase):
    """Unit tests for the Board API"""

    def create_app(self):
        app = create_app()
        yield app

    def setUp(self, app, client):

        payload = {
            "username": "Test User",
            "email": "test13@email.com",
            "password": "testPass123!"
        }

        self.user = client_post_helper(client, '/register', payload)

        login_res = client_post_helper(client, '/login', {
            "email": payload["email"],
            "password": payload["password"]
        })
        
        self.assertEqual(login_res.status_code, 200)
        self.jwt_token = json.loads(login_res.data)["token"]


    def test_board_create_no_columns(self, app, client):
        """
        Test creating a board with no columns
        Returned data should contain 
        """
        payload = {
            "name": "Test Board Name",
            "columns": []
        }

        res = client.post('/api/create_board', 
                headers={
                "Authorization": f"Bearer {self.jwt_token}"
                }, 
                data=json.dumps(payload), content_type="application/json"
            )

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertIn("user", data)
        self.assertIn("columns", data)
        self.assertIn("name", data)
        self.assertIn("_id", data)

    def test_board_create_with_columns(self, app, client):

        columns = [
            {
                "name": "Test Column One",
                "tasks": []
            },
            {
                "name": "Test Column Two",
                "tasks": []
            },
            {
                "name": "Test Column Three",
                "tasks": []
            }
        ]

        payload = {
            "name": "Test Board Name",
            "columns": columns
        }

        res = client.post(
            "api/create_board",
            headers ={
                "Authorization": f"Bearer {self.jwt_token}",
            },
            data = json.dumps(payload),
            content_type="application/json"
        )
        
        self.assertEqual(res.status_code, 200)
        
        data = json.loads(res.data)
        print("DATA:::", data)
        self.assertEqual(len(data["columns"]), 3)


    def tearDown(self, app, client):
        mongo.db.users.delete_many({})
