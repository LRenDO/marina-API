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
from oauth import verify_jwt
import methodHelpers as m


bp = Blueprint('boat', __name__, url_prefix='/boats')


@bp.route('', methods=['POST', 'GET'])
def boats_get_post():
    # Validate correct accept type
    if not request.accept_mimetypes.accept_json:
        abort(406)

    # Verify JWT
    jwt = request.headers.get("Authorization")
    user_id = verify_jwt(jwt)

    if request.method == 'POST':
        # Validate the Number of Attributes Received
        # if incorrect respond with 400 Bad Request
        content = request.get_json()   
        if len(content) != 3:
            abort(400, {"message": c.edit_errors["missing_attribute"]})

        # Create Entity
        content["owner"] = user_id
        new_boat = ds.create_entity(c.boats, content)
        new_boat = ds.add_id_self(new_boat, request, c.boats)
        query_list = [{"property": "carrier",
                       "operator": "=",
                       "value": int(new_boat["id"])}]
        new_boat["loads"] = ds.get_add_filter_query(c.loads,
                                                    query_list)
        return new_boat, 201
        
    elif request.method == 'GET':
        # Return all boats owned by owner (JWT sub)
        query_list = [{"property": "owner", "operator": "=", "value": user_id}]
        results = ds.get_filter_query(c.boats, query_list, request)
        for e in results["boats"]:
            e["loads"] = request.base_url + "/" + str(e["id"]) + "/" + \
                         c.loads
        return json.dumps(results), 200
        
    else:
        abort(405)


@bp.route('/<id>', methods=['GET', 'DELETE', 'PATCH', 'PUT'])
def boat_get_delete_patch_put(id):
    # Verify boat exists
    boat = ds.get_entity(c.boats, int(id))
    if not boat:
        abort(404, {"message": c.boat_errors["invalid_boat_id"]})

    # Verify JWT is valid
    jwt = request.headers.get("Authorization")
    user_id = verify_jwt(jwt)

    # Verify user is owner
    if boat["owner"] != user_id:
        # Sub doesn't match owner, Return 403
        abort(403, description=c.oauth_errors["not_owner"])

    elif request.method == 'GET':
        # Validate correct accept type
        if not request.accept_mimetypes.accept_json:
            abort(406)

        ds.add_id_self(boat, request, c.boats)
        # boat["id"] = int(id)
        # boat["self"] = ds.get_self_url(request, c.boats, int(id))
        query_list = [{"property": "carrier",
                       "operator": "=",
                       "value": int(id)}]
        boat["loads"] = ds.get_add_filter_query(c.loads, query_list)
        for e in boat["loads"]:
            e["self"] = ds.get_self_url(request, c.loads, e["id"])
            ds.repackage_carrier(e, request)
        return json.dumps(boat), 200
            
    elif request.method == 'DELETE':
        # If load is assigned to boat Remove from load Before Deleting
        query_list = [{"property": "carrier",
                       "operator": "=",
                       "value": int(id)}]
        results = ds.get_add_filter_query(c.loads, query_list)
        ds.edit_property(results, "carrier", None)
        ds.delete_entity(c.boats, int(id))
        return '', 204

    elif request.method == 'PATCH':
        edited_boat = m.run_patch(request, c.boats, id)
        return edited_boat, 200

    elif request.method == 'PUT':
        edited_boat = m.run_put(request, c.boats, id)
        return edited_boat, 200

    else:
        abort(405)


@bp.route('/<boat_id>/loads/<load_id>', methods=['PUT', 'DELETE'])
def load_boat_put_delete(load_id, boat_id):
    # Validate correct accept type
    if not request.accept_mimetypes.accept_json:
        abort(406)

    # Verify JWT
    jwt = request.headers.get("Authorization")
    user_id = verify_jwt(jwt)

    # Verify user is owner
    load = ds.get_entity(c.loads, int(load_id))
    boat = ds.get_entity(c.boats, int(boat_id))
    if not load or not boat:
        error_message = c.boat_errors["invalid_boat_id"] + " and/or " + \
                        c.load_errors["invalid_load_id"]
        abort(404, {"message": error_message})

    if boat["owner"] != user_id:
        # Sub doesn't match owner, Return 403
        abort(403, description=c.oauth_errors["not_owner"])
    
    if request.method == 'PUT':
        if load["carrier"] and load["carrier"] != int(boat_id):
            abort(403, description=c.load_errors["already_loaded"])
        else:
            ds.edit_property([load], "carrier", int(boat_id))
            return '', 204
            
    elif request.method == 'DELETE':
        if load["carrier"] == int(boat_id):
            ds.edit_property([load], "carrier", None)
            return '', 204

        else:
            abort(404, {"message": c.boat_errors["invalid_boat_load"]})

    else:
        abort(405)


@bp.route('/<id>/loads', methods=['GET'])
def boats_loads_get_(id):
    # Validate correct accept type
    if not request.accept_mimetypes.accept_json:
        abort(406)

    # Verify JWT
    jwt = request.headers.get("Authorization")
    user_id = verify_jwt(jwt)

    # Verify user is owner
    boat = ds.get_entity(c.boats, int(id))
    if boat["owner"] != user_id:
        # Sub doesn't match owner, Return 403
        abort(403, description=c.oauth_errors["not_owner"])

    if request.method == 'GET':
        results = {"loads": []}

        if not boat:
            abort(404, {"message": c.boat_errors["invalid_boat_id"]})
        query_list = [{"property": "carrier",
                       "operator": "=",
                       "value": int(id)}]
        results["loads"] = ds.get_add_filter_query(c.loads, query_list)
        for e in results["loads"]:
            e["self"] = ds.get_self_url(request, c.loads, e["id"])
            ds.repackage_carrier(e, request)
        return json.dumps(results), 200
    else:
        abort(405)

