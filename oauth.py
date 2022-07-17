# Author: Ren Demeis-Ortiz
# Course: CS493 Cloud Application Development (Final Project)
# Description: Oauth Routes
#
# Sources: OSU CS493 Module 4 Exploration
#          https://canvas.oregonstate.edu/courses/1870359/modules/items/22099651
from flask import request, render_template, redirect, abort, \
    Blueprint, make_response
from google.oauth2 import id_token
from google.auth import exceptions
from google.auth.transport import requests as g_req
import requests
import random
import json
import constants as c
import datastoreHelpers as ds
from urllib.parse import urlencode
import datetime as dt

bp = Blueprint('oauth', __name__, url_prefix='/oauth')


@bp.route('', methods=['GET'])
def oauth_get():
    if request.method == 'GET':
        oauth_entity = None
        if request.args.get("error"):
            abort(401, {"message": request.args["error"]})
        if not request.args.get("code"):

            # Generate Random State, Verify it's Unique and Store in Database
            random.seed()
            while True:
                state = ""
                for i in range(c.state_size):
                    state = state + random.choice(c.allowed_chars)
                query = [
                    {"property": "state", "operator": "=", "value": state}]
                oauth_entity = ds.get_add_filter_query("oauth", query)
                if not oauth_entity:
                    break
            oauth_entity = ds.create_entity("oauth", {"state": state})

            # Send Request for Access Code
            payload = c.oauth_params
            payload["state"] = state
            url_with_params = c.oauth_url + "?" + urlencode(payload)
            return redirect(url_with_params, code=303)

        elif request.args.get("state") and request.args.get("code"):
            # Check State and Send Request for Token
            query = [{"property": "state",
                      "operator": "=",
                      "value": request.args["state"]}]
            oauth_entity = ds.get_add_filter_query("oauth", query)
            if not oauth_entity:
                abort(401, {"message": c.oauth_errors["state_error"]})

            payload = c.oauth_data
            payload["code"] = request.args["code"]
            res = requests.post(c.token_url, data=payload,
                                headers=c.token_req_headers)
            res_content = json.loads(res.text)
            jwt_token = res_content["id_token"]
            if "error" in res_content:
                abort(401, {
                    "message": res_content["error"] + " " + res_content[
                        "error_description"]})

            # Get First and Last Name and State
            api_headers = {"Authorization": res_content["token_type"] + " "
                                            + res_content["access_token"]}
            res = requests.get(c.names_url, headers=api_headers)

            if res.status_code != 200:
                return res.text, res.status_code

            # Verify JWT
            id_info = id_token.verify_oauth2_token(jwt_token, g_req.Request(),
                                                   c.oauth_params["client_id"])
            res_content = json.loads(res.text)
            res_content = res_content["names"][0]
            context = {"first_name": res_content["givenName"],
                       "last_name": res_content["familyName"],
                       "creation_date": str(dt.date.today())}

            ds.create_entity(c.users, context, id_info["sub"])
            context["id_token"] = jwt_token
            context["user_id"] = id_info['sub']

            # Delete oauth Entity
            ds.delete_entity("oauth", oauth_entity[0].key.id)
            return render_template("profile.html", context=context), 200
    else:
        abort(405)
    return


def verify_jwt(jwt):
    if not jwt:
        abort(401, {"message": c.oauth_errors["missing_jwt"]})
    else:
        jwt = jwt.replace('Bearer ', '')
        # Verify JWT
        try:
            id_info = id_token.verify_oauth2_token(jwt, g_req.Request(),
                                                   c.oauth_params["client_id"])
            user_id = id_info['sub']
        except ValueError as e:
            print(e)
            abort(401, {"message": c.oauth_errors["invalid_or_expired_jwt"]})
        except exceptions.GoogleAuthError as e:
            print(e)
            abort(401, {"message": c.oauth_errors["invalid_jwt"]})

    return user_id
