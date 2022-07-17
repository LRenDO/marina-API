# Author: Ren Demeis-Ortiz
# Course: CS493 Cloud Application Development (Final Project)
# Description: Boat Routes
#
# Sources: OSU CS493 Module 4 Exploration
#          https://canvas.oregonstate.edu/courses/1870359/modules/items/22099651

from flask import abort, request, Blueprint
import json
import constants as c
import datastoreHelpers as ds

bp = Blueprint('user', __name__, url_prefix='/users')


@bp.route('', methods=['GET'])
def user_get():
    # Validate correct accept type
    if not request.accept_mimetypes.accept_json:
        abort(406)
    if request.method == 'GET':
        results = ds.get_full_collection(c.users, request)
        return json.dumps(results), 200

    else:
        abort(405)


@bp.route('/<id>', methods=['DELETE'])
def user_delete(id):
    if request.method == 'DELETE':
        ds.delete_entity(c.users, id)
        return '', 204
    else:
        abort(405)
