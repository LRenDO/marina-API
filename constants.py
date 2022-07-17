import string
import credentials as cr

boats = "boats"
loads = "loads"
users = "users"
limit = 5
allowed_chars = string.ascii_letters + string.digits
state_size = 10
oauth_url = "https://accounts.google.com/o/oauth2/v2/auth"
token_url = "https://oauth2.googleapis.com/token"
names_url = "https://people.googleapis.com/v1/people/me?personFields=names"
oauth_params = {
    "response_type": "code",
    "client_id": cr.credentials["client_id"],
    "redirect_uri": cr.credentials["redirect_uris"][1],
    "scope": "https://www.googleapis.com/auth/userinfo.profile"
   }
oauth_data = {
    "client_id": cr.credentials["client_id"],
    "client_secret": cr.credentials["client_secret"],
    "redirect_uri": cr.credentials["redirect_uris"][1],
    "grant_type": "authorization_code"
    }
token_req_headers = {"content-type": "application/x-www-form-urlencoded"}
edit_errors = {
                "missing_attribute": "The request object is missing at least"
                                     " one of the required attributes",
                "invalid_attribute_num": "Must have 1 or 2 attributes to PATCH"
                                         " the load with this load_id",
}

boat_errors = {
                "invalid_boat_id": "No boat with this boat_id exists",
                "invalid_boat_load": "Load with this load_id is not on boat "
                                     "with this boat_id"
}

load_errors = {
                "invalid_load_id": "No load with this load_id exists",
                "change_carrier": "To update carrier you must use "
                                  "GET boats/:boat_id/loads/load_id",
                "already_loaded": "The load is already assigned to a boat"
}

oauth_errors = {
    "invalid_jwt": "Invalid JWT",
    "invalid_or_expired_jwt": "Invalid or Expired JWT. Update token.",
    "missing_jwt": "Missing JWT",
    "invalid_state": "Unauthorized. State does not exist.",
    "accept_type": "Accept type must be application/json",
    "not_owner": "Protected resources can only be viewed by owner",
    "state_error": "Invalid state. Authentication process aborted."
}
