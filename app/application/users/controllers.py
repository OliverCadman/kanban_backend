

from werkzeug.security import generate_password_hash
from application.database import mongo

class User:

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = generate_password_hash(password)
    
    def _get_user_profile(self):
        return {
            "username": self.username,
            "email": self.email,
            "password": self.password
        }
    
    def register(self):
        user_data = self._get_user_profile()
    
        db_insert = mongo.db.users.insert_one(user_data)
        if db_insert:
            return True
        else:
            return False
        
