from application.database import mongo
from collections.abc import Sequence
from bson.objectid import ObjectId

from typing import List


class Board:
    """
    Model to represent a single board.
    """
    def __init__(self, user, name, columns):
        self.user = user
        self.name = name
        self.columns = columns if isinstance(columns, List) else []
    
    def _get_board(self):
        return {
            "user": self.user,
            "name": self.name,
            "columns": self.columns
        }

    def add_board(self):
        board = self._get_board()

        board_insert = mongo.db.boards.insert_one(board)
        return board_insert.inserted_id
    
    @staticmethod
    def get_users_boards(id):
        return mongo.db.boards.find({"user": ObjectId(id)})

    @staticmethod
    def find_board_by_id(id):
        return mongo.db.boards.find_one({"_id": ObjectId(id)})

    @staticmethod
    def update_board_columns(id, column_arr):
        return mongo.db.boards.update_one(
            {"_id": ObjectId(id)},
            {
                "$push": {
                    "columns": {
                        "$each": column_arr
                    }
                }
            }
        )

    @staticmethod
    def remove_board_columns(id, column_arr):

        return mongo.db.boards.update_one(
            {"_id": ObjectId(id)},
            {
                "$pull": {
                    "columns": {
                        "name": {
                            "$in": column_arr
                        }
                    }
                }
            }
        )

    @staticmethod
    def get_boards(user_id):
        return mongo.db.boards.find(
            {"user": ObjectId(user_id)}
        )

    @staticmethod
    def get_board(board_id):
        return mongo.db.boards.find_one(
            {"_id": ObjectId(board_id)}
        )
