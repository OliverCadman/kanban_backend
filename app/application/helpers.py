from bson import json_util
import json


def parse_json(data):
    """
    Helper function to serialize a User object.
    Required since ObjectId is non-JSON serializable.
    """
    return json.loads(json_util.dumps(data))

