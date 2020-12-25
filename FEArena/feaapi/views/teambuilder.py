from django.http import (
    HttpRequest, HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponseServerError,
    HttpResponseForbidden, HttpResponseNotFound
)
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
import json
import logging
from ..api.teambuilder import build


@login_required
def build_team(request: HttpRequest) -> HttpResponse:
    """
    Tries to build a new BuiltTeam for the user submitting the request, and returns the generated
    BuiltTeam in its entirety, conforming to the built_team_schema in api.teambuilder.schemas
    :param request: the HTTP request
    :return: a HTTP response with a JSON body conforming to the built_team_schema
    """
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    try:
        with transaction.atomic():
            instructions = json.load(request)
            data = build.build_team(request.user, instructions)
            return JsonResponse(data)
    except ValueError as e:
        return HttpResponseBadRequest(str(e))
    except IndexError as e:
        logging.error(e)
        return HttpResponseServerError()


@login_required
def get_teams(request: HttpResponse) -> HttpResponse:
    """
    Returns a list of all built teams belonging to the user making the request
    :param request: request, including user data
    :return: a HTTPResponse consisting of a list of BuiltTeam data conforming to the built_team_schema
    """
    print("All Teams")
    return JsonResponse(build.get_all_teams(request.user), safe=False)


@login_required
def single_team(request: HttpRequest, team_id: int) -> HttpResponse:
    """
    GET: returns just the requested team, if owned by the user making the request
        -> returns 200, 403, or 404
    DELETE: deletes the requested team, if owned by the user making the request
        -> returns 204, 403, or 404
    """
    print("Single Team")
    if request.method == 'GET':
        try:
            data = build.get_team(request.user, team_id)
            return JsonResponse(data)
        except ValueError:
            return HttpResponseForbidden()
        except ObjectDoesNotExist:
            return HttpResponseNotFound()
    elif request.method == 'DELETE':
        try:
            with transaction.atomic():
                build.delete_team(request.user, team_id)
                return HttpResponse(status=204)
        except ValueError:
            return HttpResponseForbidden()
        except ObjectDoesNotExist:
            return HttpResponseNotFound()
    else:
        return HttpResponseNotAllowed(['GET', 'DELETE'])
