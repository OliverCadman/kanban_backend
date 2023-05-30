from application.database import mongo
from pymongo.collection import ReturnDocument
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
            {"user": ObjectId(user_id)},
            {
                "user": 0
            }
        )

    @staticmethod
    def get_board(board_id):
        return mongo.db.boards.find_one(
            {"_id": ObjectId(board_id)}
        )

    @staticmethod
    def get_task(board_id, column_name, task_id):
        return list(mongo.db.boards.aggregate([
            {
                "$match": {
                    "_id": ObjectId(board_id)
                }
            },
            {
                "$unwind": "$columns"
            },
            {
                "$match": {
                    "columns.name": column_name
                }
            },
            {
                "$replaceRoot": {
                    "newRoot": "$columns"
                }
            },
            {
                "$unwind": "$tasks"
            }, 
            {
                "$match": {
                    "tasks._id": ObjectId(task_id)
                }
            },
            {
                "$replaceRoot": {
                    "newRoot": "$tasks"
                }
            }
        ])
        )

    @staticmethod
    def update_task_add_subtasks(board_id, column_name,
                                 task_id, subtask_data):
        """
        Update title and description of task.
        Push new subtasks into subtask array.
        subtask_data handles and array containing an arbitrary number of subtasks.
        """

        return mongo.db.boards.find_one_and_update(
                {"_id": ObjectId(board_id)},
                {
                    "$push": {
                        "columns.$[t].tasks.$[i].subtasks": {
                            "$each": subtask_data
                        }
                    }
                },
                array_filters=[
                    {"t.name": column_name},
                    {"i._id": ObjectId(task_id)}
                ],
                return_document=ReturnDocument.AFTER
            )

    @staticmethod
    def update_task_meta(board_id, column_name, task_id, 
                         new_title, new_description):
        """Update title and description of task."""
        return mongo.db.boards.find_one_and_update(
            {"_id": ObjectId(board_id)},
            {
                "$set": {
                    "columns.$[t].tasks.$[i].title": new_title,
                    "columns.$[t].tasks.$[i].description": new_description
                }
            },
             array_filters=[
                    {"t.name": column_name},
                    {"i._id": ObjectId(task_id)}
                ],
            return_document=ReturnDocument.AFTER
        )

    @staticmethod
    def update_task_remove_subtasks(board_id, column_name,
                                    task_id, subtasks_to_remove):
        """
        Update title and description of given task.
        Pull subtasks from the subtask array.
        If an ID of a given subtask is included in the array 'subtasks_to_remove',
        pull it from the array.
        """

        return mongo.db.boards.find_one_and_update(
            {"_id": ObjectId(board_id)},
            {
                "$pull": {
                    "columns.$[t].tasks.$[i].subtasks": {
                        "_id": {
                            "$in": subtasks_to_remove
                        }
                    }
                }
            },
            array_filters=[
                {"t.name": column_name},
                {"i._id": ObjectId(task_id)}
            ],
            return_document=ReturnDocument.AFTER
        )
    
    @staticmethod
    def update_subtask_title(board_id, column_name, task_id, subtasks_to_update):
        for subtask in subtasks_to_update:
            mongo.db.boards.find_one_and_update(
                {"_id": ObjectId(board_id)},
                {
                    "$set": {
                        "columns.$[t].tasks.$[i].subtasks.$[j].title": subtask["title"]
                    }
                },
                array_filters=[
                    {"t.name": column_name},
                    {"i._id": ObjectId(task_id)},
                    {"j._id": ObjectId(subtask["_id"].get("$oid"))}
                ]
            )
    

    def update_task_status(board_id, task_id, 
                           prev_status, new_status, new_task):

        mongo.db.boards.find_one_and_update(
            {
                "_id": ObjectId(board_id),
                "columns.name": prev_status
            },
            {
    
                "$pull": {
                    "columns.$[t].tasks": {
                        "_id": ObjectId(task_id)
                    }
                },
                "$push": {
                    "columns.$[i].tasks": new_task
                }
            },
            array_filters=[
                {"t.name": prev_status},
                {"i.name": new_status}
            ]
        )
    
        return mongo.db.boards.find_one_and_update(
            {"_id": ObjectId(board_id)},
            {
                 "$set": {
                    "columns.$[i].tasks.$[j].status": new_status
                },
            },
            array_filters=[
                {"i.name": new_status},
                {"j._id": ObjectId(task_id)}
            ],
            return_document=ReturnDocument.AFTER
        )

    @staticmethod
    def add_task_to_column(board_id, column_name, task_data): 
          return mongo.db.boards.find_one_and_update(
                {
                    "_id": ObjectId(board_id),
                    "columns.name": column_name
                },
                {
                    "$push": {
                        "columns.$.tasks": task_data
                    }
                }
            )

    @staticmethod
    def remove_task_from_column(board_id, column_name, task_id):
        return mongo.db.boards.find_one_and_update(
            {
                "_id": ObjectId(board_id),
                "columns.name": column_name
            },
            {
                "$pull": {
                    "columns.$.tasks": {
                        "_id": ObjectId(task_id)
                    }
                }
            }
        )
