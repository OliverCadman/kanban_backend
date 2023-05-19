from application import create_app
from application.test_helpers import client_post_helper
from application.database import mongo
import flask_unittest


from application.boards.models import Board

import json
from bson.objectid import ObjectId
from application.helpers import parse_json


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
        """Test removing a subtask from a given column is successful."""

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

    def test_update_task_title_add_subtasks(self, app, client):
        """Test updating a task title and subtasks is successful."""
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


        payload_2 = {
            "title": "Test Task Title 2",
            "description": "Test Task Description",
            "subtasks": subtasks
        }

        client.patch(
            f"/api/add_task/{self.board_id}/{self.test_column_1}",
            headers={
                "Authorization": f"Bearer {self.jwt_token}"
            },
            data=json.dumps(payload_2),
            content_type="application/json"
        )

        task_id = data["columns"][0]["tasks"][0]["_id"].get("$oid")

        current_subtasks = Board.get_task(self.board_id, self.test_column_1, task_id)[0]["subtasks"]

        subtasks_to_add = [
            {
                "title": "Test Subtask Title 4",
                "isCompleted": False
            },
            {
                "title": "Test Subtask Title 5",
                "isCompleted": False
            }
        ]

        patch_payload = {
            "title": "New Task Title",
            "description": "Test Task Description",
            "subtasks": current_subtasks + subtasks_to_add
        }

        res = client.patch(
            f"/api/update_task/{self.board_id}/{self.test_column_1}/{task_id}",
            headers={
                "Authorization": f"Bearer {self.jwt_token}"
            },
            data=json.dumps(parse_json(patch_payload)),
            content_type="application/json"
        )

        self.assertEqual(res.status_code, 200)

        data = json.loads(res.data)
        task = data["columns"][0]["tasks"][0]

        self.assertEqual(task["title"], patch_payload["title"])
        self.assertEqual(task["description"], patch_payload["description"])
        self.assertEqual(len(task["subtasks"]), 5)
    
    def test_update_task_remove_subtasks(self, app, client):
        """Test updating a task title, description and removing subtasks is successful."""
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
        task_id = data["columns"][0]["tasks"][0]["_id"].get("$oid")

        current_subtasks = Board.get_task(self.board_id, self.test_column_1, task_id)[0]["subtasks"]

        # Remove all but one subtask from the list
        patched_subtasks = current_subtasks[:-2]
        
        patched_payload = {
            "title": "New Task Title",
            "description": "New Task Description",
            "subtasks": patched_subtasks
        }

        res = client.patch(
            f"/api/update_task/{self.board_id}/{self.test_column_1}/{task_id}",
            headers={
                "Authorization": f"Bearer {self.jwt_token}"
            },
            data=json.dumps(parse_json(patched_payload)),
            content_type="application/json"
        )

        self.assertEqual(res.status_code, 200)

        data = json.loads(res.data)
        task = data["columns"][0]["tasks"][0]

        self.assertEqual(task["title"], patched_payload["title"])
        self.assertEqual(task["description"], patched_payload["description"])

        # Confirm only one subtask in the returned collection.
        self.assertEqual(len(task["subtasks"]), 1)
    
    def test_update_task_add_tasks_change_existing_task_titles(self, app, client):
        """
        Test the following are successful:
            Changing a task title
            Adding subtasks
            Changing existing subtask titles.
        """
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
        task_id = data["columns"][0]["tasks"][0]["_id"].get("$oid")

        current_subtasks = Board.get_task(self.board_id, self.test_column_1, task_id)[0]["subtasks"]

        # New subtasks
        new_subtasks = [
            {
                "title": "Test Subtask 4",
                "isCompleted": False
            },
            {
                "title": "Test Subtask 5",
                "isCompleted": False
            }
        ]

        # Change title of first two existing subtasks
        current_subtasks[0]["title"] = "New Subtask Title 1"
        current_subtasks[1]["title"] = "New Subtask Title 2"

        patch_payload = {
            "title": "New Task Title",
            "description": "New Task Description",
            "subtasks": current_subtasks + new_subtasks
        }

        res = client.patch(
            f"/api/update_task/{self.board_id}/{self.test_column_1}/{task_id}",
            headers={
                "Authorization": f"Bearer {self.jwt_token}"
            },
            data=json.dumps(parse_json(patch_payload)),
            content_type="application/json"
        )

        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        
        task = data["columns"][0]["tasks"][0]
        self.assertEqual(len(task["subtasks"]), 5)
        self.assertEqual(task["title"], patch_payload["title"])
        self.assertEqual(task["description"], patch_payload["description"])
        self.assertEqual(task["subtasks"][0]["title"], current_subtasks[0]["title"])
        self.assertEqual(task["subtasks"][1]["title"], current_subtasks[1]["title"])


    def test_update_task_remove_tasks_change_existing_task_titles(self, app, client):
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
        task_id = data["columns"][0]["tasks"][0]["_id"].get("$oid")

        current_subtasks = Board.get_task(self.board_id, self.test_column_1, task_id)[0]["subtasks"]

        patched_subtasks = current_subtasks[:-2]
        patched_subtasks[0]["title"] = "New Subtask Title"

        patch_payload = {
            "title": "New Task Title",
            "description": "New Task Description",
            "subtasks": patched_subtasks
        }

        res = client.patch(
            f"/api/update_task/{self.board_id}/{self.test_column_1}/{task_id}",
            headers={
                "Authorization": f"Bearer {self.jwt_token}"
            },
            data=json.dumps(parse_json(patch_payload)),
            content_type="application/json"
        )

        self.assertEqual(res.status_code, 200)
        
        data = json.loads(res.data)
        task = data["columns"][0]["tasks"][0]
        self.assertEqual(len(task["subtasks"]), 1)
        self.assertEqual(task["subtasks"][0]["title"], "New Subtask Title")
        self.assertEqual(task["title"], patch_payload["title"])
        self.assertEqual(task["description"], patch_payload["description"])

    def test_add_task_unauthorized_user_error(self, app, client):
        pass

    def tearDown(self, app, client):
        mongo.db.users.delete_many({})
        mongo.db.boards.delete_many({})
