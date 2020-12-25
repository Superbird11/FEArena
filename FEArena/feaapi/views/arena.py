from django.http import (
    HttpRequest, HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponseNotFound,
)
from django.contrib.auth.decorators import login_required
from django.db import transaction
import json
from ..api.arena import arena


# POST
@login_required
def request_match(request: HttpRequest) -> HttpResponse:
    """
    Responds with a single token, which should be used for querying match status
    in the future.
    :return: a response containing a single token with which to request match status,
        or a 400 error if user has already requested a match
    """
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    req_body = json.load(request)
    try:
        with transaction.atomic():
            request_id = arena.request_match(request.user, req_body)
            return HttpResponse(request_id, status=200)
    except ValueError as e:
        return HttpResponseBadRequest(e)

# GET
@login_required
def check_match_request_status(request: HttpRequest, url_request_id: str) -> HttpResponse:
    """
    Given the urlencoded request_id, check the match request status, returning a
    HTTP 304 if the match hasn't started yet, or a HTTP 200 otherwise.
    :param request: request, including user info
    :param url_request_id: match request ID, from urlencoded value
    :return: HTTP 304 if match hasn't started yet, or HTTP 200 response containing
        a single token which is the arena ID, so the user can request arena info
    """
    try:
        request_id = int(url_request_id)
        arena_id = arena.check_request_status(request.user, request_id)
        print(arena_id)
        if arena_id is None:
            return HttpResponse(status=304)
        return HttpResponse(arena_id, status=200)
    except ValueError:
        return HttpResponseBadRequest("No match request with the given id exists for this user")


# GET
def get_arena_data(request: HttpRequest, arena_id: str) -> HttpResponse:
    """
    Returns the current state of the ActiveArena with the given ID, as JSON
    conforming to the active_arena_schema defined in api.arena.schemas
    :param request: unused, the HTTP request
    :param arena_id: the urlencoded arena id
    :return: a HTTP 404 if the arena does not exist, or a HTTP 200 containing
        active arena data, conforming to active_arena_schema from api.arena.schemas
    """
    try:
        return JsonResponse(arena.get_arena_info(arena_id))
    except ValueError:
        return HttpResponseNotFound()


# POST
@login_required
def submit_action(request: HttpRequest, arena_id: str) -> HttpResponse:
    """
    Submits and processes the action contained in the request (must conform to
    the action_input_schema defined in api.arena.schemas), and if successful
    returns the results of the action (conforming to the action_output_schema)
    :param request: POST request including user info and request info
    :param arena_id: the id of the arena this request is being made for
    :return: a HTTP 400 if there's a problem (error as the body), or a HTTP 200
        containing JSON conforming to action_output_schema
    """
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    try:
        with transaction.atomic():
            return JsonResponse(arena.process_phase(
                request.user,
                arena_id,
                json.load(request)
            ))
    except ValueError as e:
        return HttpResponseBadRequest(e)
