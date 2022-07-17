# Author: Ren Demeis-Ortiz
# Course: CS493 Cloud Application Development (Final Project)
# Description: API that assigns loads to boats where boats have owners and
#               boats can only be accessed by owner's JWT.
#
# Sources: OSU CS493 Module 4 Exploration
#          https://canvas.oregonstate.edu/courses/1870359/modules/items/22099651
import boat
import load
import oauth
import users
from flask import Flask, request, render_template, make_response
import json
import datastoreHelpers as ds
import constants as c
import re

app = Flask(__name__)
app.register_blueprint(boat.bp)
app.register_blueprint(load.bp)
app.register_blueprint(oauth.bp)
app.register_blueprint(users.bp)

#ds.remove_counter(c.boats)
#ds.remove_counter(c.loads)
ds.initialize_counter(c.loads)
ds.initialize_counter(c.boats)

@app.route('/')
def index():
    login_url = request.host_url + "oauth"
    return render_template("index.html", link_url=login_url), 200


@app.errorhandler(400)
def handle_bad_request(error):
    if "message" not in error.description:
        error_message = ""
    else:
        error_message = error.description['message']
    return json.dumps({"Error": error_message}), 400


@app.errorhandler(401)
def handle_not_found(error):
    error_message = json.dumps({"Error": error.description['message']})
    return error_message, 401


@app.errorhandler(403)
def handle_not_found(error):
    return json.dumps({"Error": error.description}), 403


@app.errorhandler(404)
def handle_not_found(error):
    if "message" not in error.description:
        error_message = "Page not found"
    else:
        error_message = error.description['message']
    return json.dumps({"Error": error_message}), 404


@app.errorhandler(405)
def handle_method_not_allowed(error):
    is_load = re.search("/loads/", request.path)
    is_boat = re.search("/boats/", request.path)
    allowed_methods = ""

    response = make_response(json.dumps({"Error": error.description}))
    if request.path == "/boats" or request.path == "/loads":
        allowed_methods = "POST, GET"
    elif is_boat or is_load:
        allowed_methods = "GET, DELETE, PATCH, PUT"
    elif is_boat and is_load:
        allowed_methods = "DELETE, PUT"
    elif request.path == "/oauth" or request.path == "/users":
        allowed_methods = "GET"
    response.headers.set('Allow', allowed_methods)
    response.status_code = 405
    return response


@app.errorhandler(406)
def handle_not_found(error):
    error_message = json.dumps({"Error": c.oauth_errors["accept_type"]})
    return error_message, 406


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
