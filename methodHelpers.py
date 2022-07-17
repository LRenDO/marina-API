# Author: Ren Demeis-Ortiz
# Course: CS493 Cloud Application Development (Final Project)
# Description: Helper functions to perform route method actions
import datastoreHelpers as ds
import constants as c
from flask import abort


def in_patch_bounds(length):
    """
    Checks if integer equals 3

    :param length: (int) integer to check if it's within bounds
    :return: bool true if it is 3 otherwise false
    """
    if length > 2 or length < 1:
        return False
    else:
        return True


def in_put_bounds(length):
    """
    Checks if integer equals 3

    :param length: (int) integer to check if it's within bounds
    :return: bool true if it is 3 otherwise false
    """
    if length != 3:
        return False
    else:
        return True


def run_patch(request, entity_kind, id):
    """
    Helper that passes length bound function for patch method

    :params:
            entity_kind (string) is the type of entity
            request (flask request) flask request to pull url information from
            id (int) id of entity to be changed
    :returns: datastore entity entity that was edited
    """
    edited_entity = run_edit(in_patch_bounds, request, entity_kind, id)
    return edited_entity


def run_put(request, entity_kind, id):
    """
    Helper that passes length bound function for put method

    :params:
            entity_kind (string) is the type of entity
            request (flask request) flask request to pull url information from
            id (int) id of entity to be changed
    :returns: datastore entity entity that was edited
    """
    edited_entity = run_edit(in_put_bounds, request, entity_kind, id)
    return edited_entity


def run_edit(in_bounds, request, entity_kind, id):
    """
    Uses datstoreHelper module to edit datstore entity properties

    :params:
            in_bounds (func) function that returns a bool that says if length
                            is within the bounds
            entity_kind (string) is the type of entity
            request (flask request) flask request to pull url information from
            id (int) id of entity to be changed
    :returns: datastore entity entity that was edited
    """
    # Validate correct accept type
    if not request.accept_mimetypes.accept_json:
        abort(406)

    # Validate attribute number and does not edit carrier
    content = request.get_json()
    if not in_bounds(len(content)):
        if request.method == "PATCH":
            abort(400, {"message": c.edit_errors["invalid_attribute_num"]})
        elif request.method == "PUT":
            abort(400, {"message": c.edit_errors["missing_attribute"]})
    elif "carrier" in content:
        abort(403, description=c.load_errors["change_carrier"])

    # Update and Return Entity
    entity = ds.get_entity(entity_kind, int(id))
    edited_entity = ds.edit_entity(entity, content)
    edited_entity = ds.add_id_self(edited_entity, request, entity_kind)

    return edited_entity
