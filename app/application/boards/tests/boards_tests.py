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
        """
        payload = {
            "name": "Test Board Name",
            "columns": []
        }

        res = client.post('/api/create_board/', 
                headers={
                "Authorization": f"Bearer {self.jwt_token}"
                }, 
                data=json.dumps(payload), content_type="application/json"
            )

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 201)
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
            "api/create_board/",
            headers ={
                "Authorization": f"Bearer {self.jwt_token}",
            },
            data = json.dumps(payload),
            content_type="application/json"
        )
        
        self.assertEqual(res.status_code, 201)
        
        data = json.loads(res.data)

        self.assertEqual(len(data["columns"]), 3)
    
    def test_board_update_columns(self, app, client):
        """Test PATCH request to add columns to existing board."""

        payload = {
            "name": "Test Board Name",
            "columns": [
                {
                    "name": "Test Column 1",
                    "tasks": []
                }, 
                {
                    "name": "Test Column 2",
                    "tasks": []
                }
            ]
        }

        res = client.post('/api/create_board/', 
                headers={
                "Authorization": f"Bearer {self.jwt_token}"
                }, 
                data=json.dumps(payload), content_type="application/json"
            )

        data = json.loads(res.data)
        new_columns = [
            {
                "name": "Test Column 3",
                "tasks": []
            },
            {
                "name": "Test Column 4",
                "tasks": []
            }
        ]

        payload = {
            "columns_to_add": new_columns
        }

        board_id = data["_id"].get('$oid')

        res = client.patch(
            f"/api/update_board_columns/{board_id}",
            headers={
                "Authorization": f"Bearer {self.jwt_token}"
            },
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(len(data["columns"]), 4)

        for i, column in enumerate(data["columns"]):
            self.assertEqual(column["name"], f"Test Column {i + 1}")

    def test_board_remove_columns(self, app, client):
        """Test removing columns from an existing board"""

        payload = {
            "name": "Test Board Name",
            "columns": [
                {
                    "name": "Test Column 1",
                    "tasks": []
                }, 
                {
                    "name": "Test Column 2",
                    "tasks": []
                },
                {
                    "name": "Test Column 3",
                    "tasks": []
                },
                {
                    "name": "Test Column 4",
                    "tasks": []

                }
            ]
        }

        res = client.post('/api/create_board/', 
                headers={
                "Authorization": f"Bearer {self.jwt_token}"
                }, 
                data=json.dumps(payload), content_type="application/json"
            )

        self.assertEqual(res.status_code, 201)
        data = json.loads(res.data)
        board_id = data["_id"].get("$oid")

        columns_to_remove = ["Test Column 4", "Test Column 3", "Test Column 2"]
        column_ids = []
        for v in data["columns"]:
            if v["name"] in columns_to_remove:
                column_ids.append(v["name"])
        
        payload = {
            "columns_to_remove": column_ids
        }

        res = client.patch(
            f"/api/update_board_columns/{board_id}",
            headers = {
                "Authorization": f"Bearer {self.jwt_token}"
            },
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
    
        self.assertEqual(len(data["columns"]), 1)
        self.assertEqual(data["columns"][0]["name"], "Test Column 1")
    
    def test_list_boards(self, app, client):
        """Test retrieving list of board names (with IDs) is successful"""

        # Add first board
        payload = {
            "name": "Test Board Name 1",
            "columns": []
        }

        res = client.post(
            "/api/create_board/",
            headers={
                "Authorization": f"Bearer {self.jwt_token}"
            },
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(res.status_code, 201)

        # Add second board
        payload = {
            "name": "Test Board Name 2",
            "columns": []
        }
        
        res = client.post(
            "/api/create_board/",
            headers={
                "Authorization": f"Bearer {self.jwt_token}"
            },
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(res.status_code, 201)

        res = client.get(
            "/api/list_boards",
            headers={
                "Authorization": f"Bearer {self.jwt_token}"
            }
        )

        self.assertEqual(res.status_code, 200)
        
        data = json.loads(res.data)
        self.assertEqual(len(data), 2)

        for board in data:
            self.assertIn("_id", board)
            self.assertIn("name", board)
            self.assertNotIn("user", board)
            self.assertNotIn("columns", board)
        

    def tearDown(self, app, client):
        mongo.db.users.delete_many({})
        mongo.db.boards.delete_many({})
