"""Helper functions for unit tests"""
import json

def client_post_helper(client, endpoint, data):
    return client.post(
        endpoint, data=json.dumps(data), content_type='application/json')