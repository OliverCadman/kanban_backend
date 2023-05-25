from flask import Blueprint, session, request, jsonify
from werkzeug.exceptions import HTTPException
from flask_cors import CORS
from flask_jwt_extended import (
    jwt_required, 
    get_jwt_identity,
    get_jwt,
    set_access_cookies,
    create_access_token
    )

from application.users.models import User
from application.boards.models import Board
from bson.objectid import ObjectId

from application.helpers import parse_json

from datetime import datetime, timedelta, timezone


boards = Blueprint('boards', __name__)

CORS(boards, supports_credentials=True, resources=r"/api/*")

@boards.after_request
def refresh_expiring_jwts(response):

    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        return response
    

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



@boards.route('/api/list_boards', methods=["GET"])
@jwt_required()
def list_boards():
    user_email = get_jwt_identity()
    user = User.find_user_no_password(user_email)

    # if user_email != session["user_email"]:
    #     return jsonify({
    #           "msg": "You are not authorized to access another user's boards."
    #     }), 401

    if user is not None:
        board_collection = []
        boards = Board.get_boards(user["_id"])
        for board in boards:
            board_collection.append(board)

        print("BOARD COLLECTION", board_collection)
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
    new_task_title = data["title"]
    new_task_description = data["description"]

    subtasks_to_update = []
    for subtask in data["subtasks"]:
        for current_subtask in current_task[0]["subtasks"]:
            if subtask.get("_id") is not None and \
                (ObjectId(subtask.get("_id").get("$oid")) == current_subtask["_id"]) and \
                    subtask["title"] != current_subtask["title"]:
                subtasks_to_update.append(subtask)
    
    if len(subtasks_to_update) > 0:
        Board.update_subtask_title(board_id, column_name, task_id, subtasks_to_update)

    updated_board = None

    # If there are more subtasks in request payload than in the current collection
    if len(current_subtasks) < len(incoming_subtasks):
        subtasks_to_add = []
        for subtask in incoming_subtasks:
            if not "_id" in subtask:
                # Update current task with new subtasks
                subtasks_to_add.append(subtask)
        
        updated_board = Board.update_task_add_subtasks(
            board_id, column_name, task_id, subtasks_to_add,
            new_task_title, new_task_description)

    # If these are less sub tasks in request payload than in current collection
    if len(current_subtasks) > len(incoming_subtasks):
        subtask_ids_to_remove = []
        for incoming_subtask in incoming_subtasks:
            subtask_id = incoming_subtask["_id"].get("$oid")
            subtask_ids_to_remove.append(ObjectId(subtask_id))

        subtasks_to_remove = []

        for subtask in current_subtasks:

            if subtask["_id"] not in subtask_ids_to_remove:
                subtasks_to_remove.append(subtask["_id"])

        updated_board = Board.update_task_remove_subtasks(
            board_id, column_name, task_id, subtasks_to_remove,
            new_task_title, new_task_description
        )
    
    return parse_json(updated_board), 200


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
