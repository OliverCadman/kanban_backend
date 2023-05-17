from application import create_app
from application.test_helpers import client_post_helper
from application.database import mongo
import flask_unittest

import json


class TaskAPITests(flask_unittest.AppClientTestCase):

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

        board_payload = {
            "name": "Test Board Name",
            "columns": columns
        }

        res = client.post(
            "api/create_board/",
            headers ={
                "Authorization": f"Bearer {self.jwt_token}",
            },
            data = json.dumps(board_payload),
            content_type="application/json"
        )
        
        self.assertEqual(res.status_code, 201)
        
        data = json.loads(res.data)
        self.board_id = data["_id"].get("$oid")
        self.test_column_1 = data["columns"][0]["name"]
        self.test_column_2 = data["columns"][1]["name"]
    
    def test_add_task_no_subtasks(self, app, client):
        """
        Test adding a task to a given column is successful.

        Column located by column name, as a board's column names
        must be unique.

        First test adding a task to the first column.
        Second test adding a task to the second column.
        """

        payload = {
            "title": "Test Task Title",
            "description": "Test Task Description",
            "subtasks": []
        }

        res = client.patch(
            f"/api/add_task/{self.board_id}/{self.test_column_1}",
            headers={
                "Authorization": f"Bearer {self.jwt_token}"
            },
            data=json.dumps(payload),
            content_type="application/json"
            )
        
        self.assertEqual(res.status_code, 200)
        
        data = json.loads(res.data)

        self.assertEqual(len(data["columns"][0]["tasks"]), 1)
        self.assertEqual(len(data["columns"][1]["tasks"]), 0)
        self.assertEqual(data["columns"][0]["tasks"][0]["title"], payload["title"])
        self.assertEqual(data["columns"][0]["tasks"][0]["description"], payload["description"])
        self.assertIn("subtasks", data["columns"][0]["tasks"][0])


        payload_2 = {
            "title": "Test Second Task Title",
            "description": "Test Second Task Description",
            "subtasks": []
        }

        res = client.patch(
            f"/api/add_task/{self.board_id}/{self.test_column_2}",
            headers={
                "Authorization": f"Bearer {self.jwt_token}"
            },
            data=json.dumps(payload_2),
            content_type="application/json"
            )
        
        self.assertEqual(res.status_code, 200)
        
        data = json.loads(res.data)

        self.assertEqual(len(data["columns"][1]["tasks"]), 1)
        self.assertEqual(len(data["columns"][2]["tasks"]), 0)
        self.assertEqual(data["columns"][1]["tasks"][0]["title"], payload_2["title"])
        self.assertEqual(data["columns"][1]["tasks"][0]["description"], payload_2["description"])
        self.assertIn("subtasks", data["columns"][1]["tasks"][0])


    def test_add_task_with_subtasks(self, app, client):
        
        subtasks = [
            {
                "title": "Test Subtask Title 1",
                "isCompleted": False,
            },
            {
                "title": "Test Subtask Title 2",
                "isCompleted": False
            },
            {
                "title": "Test Subtask Title 3",
                "isCompleted": False
            }
        ]

        payload = {
            "title": "Test Task Title",
            "description": "Test Task Description",
            "subtasks": subtasks
        }

        res = client.patch(
            f"/api/add_task/{self.board_id}/{self.test_column_1}",
            headers={
                "Authorization": f"Bearer {self.jwt_token}"
            },
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(res.status_code, 200)

        data = json.loads(res.data)
        self.assertEqual(len(data["columns"][0]["tasks"]), 1)
        self.assertEqual(data["columns"][0]["tasks"][0]["title"], payload["title"])
        self.assertEqual(data["columns"][0]["tasks"][0]["description"], payload["description"])

        subtasks_data = data["columns"][0]["tasks"][0]["subtasks"]
        self.assertEqual(len(subtasks_data), 3)

        for k, v in payload.items():
            if k in subtasks_data:
                self.assertEqual(getattr(subtasks_data, k), v)

    def test_remove_task(self, app, client):
        payload = {
            "title": "Test Task Title",
            "description": "Test Task Description",
            "subtasks": []
        }

        res = client.patch(
            f"/api/add_task/{self.board_id}/{self.test_column_1}",
            headers={
                "Authorization": f"Bearer {self.jwt_token}"
            },
            data=json.dumps(payload),
            content_type="application/json"
            )
        
        self.assertEqual(res.status_code, 200)
        
        data = json.loads(res.data)
        self.assertEqual(len(data["columns"][0]["tasks"]), 1)
        self.assertEqual(data["columns"][0]["tasks"][0]["title"], payload["title"])
        self.assertEqual(data["columns"][0]["tasks"][0]["description"], payload["description"])
        self.assertIn("subtasks", data["columns"][0]["tasks"][0])

        task_to_remove_id = data["columns"][0]["tasks"][0]["_id"]

        payload = {
            "task_id": task_to_remove_id.get("$oid")
        }

        res = client.post(
            f"/api/remove_task/{self.board_id}/{self.test_column_1}",
            headers={
                "Authorization": f"Bearer {self.jwt_token}"
            },
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(len(data["columns"][0]["tasks"]), 0)

    def test_add_task_unauthorized_user_error(self, app, client):
        pass
