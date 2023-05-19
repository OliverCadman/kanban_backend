from flask import Blueprint, session, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from application.users.models import User
from application.boards.models import Board
from bson.objectid import ObjectId

from application.helpers import parse_json


boards = Blueprint('boards', __name__)


@boards.route('/api/create_board/', methods=["POST"])
@jwt_required()
def add_board():
    """
    POST route to create a new board.
    If are included in POST request, iterate over and
    create ObjectId() for each column object, and insert the column array
    along with board meta details.
    """
    if request.method == "POST":
        user_email = get_jwt_identity()
        user_profile = User.find_user_no_password(user_email)

        
        if user_profile is not None:
            data = request.json

            board_name = data["name"]
            board_columns = data.get("columns", [])

            if board_columns or len(board_columns) > 0:
                for column in board_columns:
                    column['_id'] = ObjectId()
        

            board = Board(user_profile['_id'], board_name, board_columns)
            inserted_board_id = board.add_board()

            inserted_board = Board.find_board_by_id(inserted_board_id)

            return parse_json(inserted_board), 201

        return 'Error', 404


@boards.route('/api/get_boards', methods=["GET"])
@jwt_required()
def get_boards():
    user_email = get_jwt_identity()
    user = User.find_user_no_password(user_email)

    if user_email != session["user_email"]:
        return jsonify({
              "msg": "You are not authorized to access another user's boards."
        }), 401

    if user is not None:
        board_collection = []
        boards = Board.get_boards(user["_id"])
        for board in boards:
            board_collection.append(board)
        return parse_json(board_collection), 200


@boards.route("/api/get_board/<board_id>", methods=["GET"])
@jwt_required()
def get_board(board_id):
    user_email = get_jwt_identity()
    user = User.find_user_no_password(user_email)

    if user["email"] != session["user_email"]:
            return jsonify({
              "msg": "You are not authorized to access another user's boards."
        }), 401
    
    board = Board.get_board(board_id)
    if board:
        return parse_json(board), 200
    else:
        return jsonify({
            "msg": "Sorry, the board does not exist"
        }), 400


@boards.route('/api/update_board_columns/<board_id>', methods=["PATCH"])
@jwt_required()
def update_board_columns(board_id):
    """
    Add or remove columns from a given board.
    """

    user_email = get_jwt_identity()
    user_profile = User.find_user_no_password(user_email)

    if user_profile is not None:

        data = request.json
        
        if "columns_to_add" in data:
            columns_to_add = data["columns_to_add"]
            for column in columns_to_add:
                column["_id"] = ObjectId()

            Board.update_board_columns(board_id, columns_to_add)
        else:
            columns_to_remove = data["columns_to_remove"]
            Board.remove_board_columns(board_id, columns_to_remove)
        updated_board = Board.find_board_by_id(board_id)
        return parse_json(updated_board), 200


@boards.route('/api/add_task/<board_id>/<column_name>', methods=["POST", "PATCH"])
@jwt_required()
def add_task(board_id, column_name):
    """
    Add tasks for a given column.
    The task's column is referenced by the column name,
    under the board ID.
    """

    user_email = get_jwt_identity()
    user_profile = User.find_user_no_password(user_email)

    if user_profile["email"] != session["user_email"]:
        return jsonify({
            "msg": "You are not authorized to access another user's boards."
    }), 401

    task = request.json
    task["_id"] = ObjectId()

    if len(task["subtasks"]) > 0:
        for subtask in task["subtasks"]:
            subtask["_id"] = ObjectId()

    Board.add_task_to_column(board_id, column_name, task)
    updated_board = Board.find_board_by_id(board_id)
    return parse_json(updated_board), 200


@boards.route("/api/update_task/<board_id>/<column_name>/<task_id>", methods=["PATCH"])
@jwt_required()
def update_task(board_id, column_name, task_id):
    """
    Update a given task.

    Task is referenced from the column by ID.
    Column is referenced from board by unique column name.
    Board is referenced by ID.

    Handles changing a task title, description and adding/removing
    of subtasks.
    """

    user_email = get_jwt_identity()

    if user_email != session["user_email"]:
        return jsonify({
            "msg": "You are not authorized to access another user's boards."
    }), 401

    current_task = Board.get_task(board_id, column_name, task_id)

    
    data = request.json

    current_subtasks = current_task[0]["subtasks"]
    incoming_subtasks = data["subtasks"]

    # If there are more subtasks in request payload than in the current collection
    if len(current_subtasks) < len(incoming_subtasks):
        subtasks_to_add = []
        for subtask in incoming_subtasks:
            if not "_id" in subtask:
                # Update current task with new subtasks
                subtasks_to_add.append(subtask)
        
        updated_board = Board.add_subtasks_to_task(
            board_id, column_name, task_id, subtasks_to_add)
        
        return parse_json(updated_board), 200

        

    # If these are less sub tasks in request payload than in current collection
    # if len(current_subtasks) > len(incoming_subtasks):
    #     subtasks_to_remove = []
    #     for subtask in incoming_subtasks:
            



    # If the subtask arrays are of equal length, but don't contain the same titles.



@boards.route("/api/remove_task/<board_id>/<column_name>", methods=["POST"])
@jwt_required()
def remove_task(board_id, column_name):
    """
    Remove a task from a given column.
    The task's column is referenced by the column name,
    under the board ID.
    """

    user_email = get_jwt_identity()
    user_profile = User.find_user_no_password(user_email)
    
    if user_profile["email"] != session["user_email"]:
        return jsonify({
            "msg": "You are not authorized to access another user's boards."
    }), 401

    data = request.json
    task_id = data["task_id"]

    Board.remove_task_from_column(board_id, column_name, task_id)
    updated_board = Board.find_board_by_id(board_id)

    return parse_json(updated_board), 200
