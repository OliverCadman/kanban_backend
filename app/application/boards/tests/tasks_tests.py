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
    
    def test_add_task_no_subtasks(self, app, client):
        pass

    def test_add_task_with_subtasks(self, app, client):
        pass

    def test_remove_task(self, app, client):
        pass

    def test_add_task_unauthorized_user_error(self, app, client):
        pass
