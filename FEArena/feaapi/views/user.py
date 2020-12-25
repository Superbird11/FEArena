from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.middleware.csrf import get_token
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User


def csrf(request: HttpRequest) -> HttpResponse:
    return HttpResponse(get_token(request), status=200)


def log_in(request: HttpRequest) -> HttpResponse:
    """
    :param request: HttpRequest containing login information (username and password)
    :return: HTTP 200 or HTTP 401
    """
    try:
        print("Hit the login function")
        username = request.POST['username']
        password = request.POST['password']
    except KeyError:
        return HttpResponseBadRequest('`username` or `password` was not provided')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return HttpResponse(status=200)
    else:
        return HttpResponse('This username+password combination does not exist', status=401)


@login_required
def log_out(request: HttpRequest) -> HttpResponse:
    """
    :param request: HttpRequest containing user information
    :return: HTTP 200
    """
    logout(request)
    return HttpResponse('Logged out.', status=200)


def create_account(request: HttpRequest) -> HttpResponse:
    """
    Creates an account for the user, and logs them in.
    :param request: including username and password data
    :return: HTTP 200, or HTTP 401 if the user's username/password are insufficient for some reason
    """
    try:
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email'] if 'email' in request.POST else None
    except KeyError:
        return HttpResponseBadRequest('`username` or `password` was not provided')
    User.objects.create_user(username, email, password)
    return log_in(request)
