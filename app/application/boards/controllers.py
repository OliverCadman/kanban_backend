from application.database import mongo


class Board:
    def __init__(self, name):
        self.name = name
    
    def get_board(self):
        return {
            "name": self.name
        }


class Column:
    pass


class Task:
    pass


class Subtask:
    pass