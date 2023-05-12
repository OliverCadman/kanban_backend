from application.database import mongo
from bson.objectid import ObjectId


class Board:
    """
    Model to represent a single board.
    """
    def __init__(self, user, name, columns):
        self.user = user
        self.name = name
        self.columns = columns if isinstance(columns, list) else []
    
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


class Column:
    """
    Model to represent a single column
    """
    def __init__(self, board, name, tasks):
        self.board = board
        self.name = name
        self.tasks = tasks if isinstance(tasks, list) else []

    def _get_column(self):
        return {
            "board": self.board,
            "name": self.name,
            "tasks": self.tasks
        }
    
    def add_column(self):
        column = self._get_column
        mongo.db.columns.insert_one(column)


class Task:
    pass


class Subtask:
    pass