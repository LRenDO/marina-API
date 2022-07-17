# Author: Ren Demeis-Ortiz
# Course: CS493 Cloud Application Development (Final Project)
# Description: Load Routes
#
# Sources: OSU CS493 Module 4 Exploration
#          https://canvas.oregonstate.edu/courses/1870359/modules/items/22099651
from flask import abort, request, Blueprint
import json
import constants as c
import datastoreHelpers as ds
import methodHelpers as m

bp = Blueprint('load', __name__, url_prefix='/loads')


@bp.route('', methods=['POST', 'GET'])
def loads_get_post():
    # Validate correct accept type
    if not request.accept_mimetypes.accept_json:
        abort(406)

    if request.method == 'POST':
        # Validate the Number of Attributes Received
        # if incorrect respond with 400 Bad Request
        content = request.get_json()  
        if len(content) != 3:
            abort(400, {"message": c.edit_errors["missing_attribute"]})
        content["carrier"] = None   
        new_load = ds.create_entity(c.loads, content)
        new_load["id"] = new_load.key.id
        new_load["self"] = ds.get_self_url(request, c.loads,
                                           new_load["id"])
        return new_load, 201
        
    elif request.method == 'GET':
        results = ds.get_all(c.loads, request)
        for e in results["loads"]:
            e["self"] = ds.get_self_url(request, c.loads, e["id"])
            e = ds.repackage_carrier(e, request)
        return json.dumps(results), 200
        
    else:
        abort(405)


@bp.route('/<id>', methods=['GET', 'DELETE', 'PATCH', 'PUT'])
def load_get_delete_patch_put(id):
    load = ds.get_entity(c.loads, int(id))
    if not load:
        abort(404, {"message": c.load_errors["invalid_load_id"]})

    elif request.method == 'GET':
        # Validate correct accept type
        if not request.accept_mimetypes.accept_json:
            abort(406)

        load = ds.add_id_self(load, request, c.loads)
        load = ds.repackage_carrier(load, request)
        return json.dumps(load), 200
  
    elif request.method == 'DELETE':
        ds.delete_entity(c.loads, int(id))
        return '', 204

    elif request.method == 'PATCH':
        edited_load = m.run_patch(request, c.loads, id)
        return edited_load, 200

    elif request.method == 'PUT':
        edited_load = m.run_put(request, c.loads, id)
        return edited_load, 200
    else:
        abort(405)
