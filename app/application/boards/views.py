from flask import Blueprint, session, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from application.users.models import User
from application.boards.models import Board

from bson.objectid import ObjectId

from application.json_parser import parse_json


boards = Blueprint('boards', __name__)


@boards.route('/api/create_board', methods=["POST"])
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


@boards.route('/api/update_board_columns/<board_id>', methods=["PATCH"])
@jwt_required()
def update_board_columns(board_id):
    user_email = get_jwt_identity()
    user_profile = User.find_user_no_password(user_email)

    if user_profile is not None:

        data = request.json
        
        if "columns_to_add" in data:
            columns_to_add = data["columns_to_add"]
            Board.update_board_columns(board_id, columns_to_add)
        else:
            columns_to_remove = data["columns_to_remove"]
            Board.remove_board_columns(board_id, columns_to_remove)
        updated_board = Board.find_board_by_id(board_id)
        return parse_json(updated_board), 200


