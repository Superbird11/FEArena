from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from ...models.user.PasswordResetToken import PasswordResetToken
import logging
import uuid
import email
import smtplib
import datetime
from threading import Timer

#######
# TODO
# Everything in this file is essentially improvised. Come back later when it matters, and
# revise it to work within Django's auth API
# https://docs.djangoproject.com/en/3.1/topics/auth/default/
# TODO
#######

PASSWORD_RESET_TIMER = 1800  # seconds
with open('pepper.txt') as pepper_file:
    PEPPER = pepper_file.read()


def create_user(username: str, password: str, email_address: str = None) -> None:
    """
    Creates a new user and adds them to the database.
    :param username: username, must be unique
    :param password: will be peppered, and also salted automatically
    :param email_address: [optional] for password reset
    """
    User.objects.create_user(username, email_address, password + PEPPER)


def authenticate_user(username: str, password: str) -> None:
    """
    Authenticates that a user exists. Returns the user if authentication succeeds,
    or None if it fails.
    """
    return authenticate(username=username, password=password + PEPPER)


def request_password_reset(username: str) -> bool:
    """
    Creates a password reset token to expire, and sends an email accordingly.
    If successful, returns True. If user does not have an email on file, returns False.
    If user does not exist, throws ValueError.
    """
    usr = User.objects.get(username=username)
    if not usr:
        logging.info(f"Password reset for nonexistent user `{username}` was requested")
        raise ValueError("User does not exist")
    email_address = usr.email
    if not usr.email:
        return False
    # create token
    token = PasswordResetToken()
    token.user = usr
    token.token = uuid.uuid4()
    token.expiry = datetime.datetime.now() + datetime.timedelta(seconds=PASSWORD_RESET_TIMER)
    token.save()
    # make timer to delete token once password reset timer expires
    Timer(PASSWORD_RESET_TIMER + 60, lambda: token.delete()).start()
    # send email
    msg = email.message.EmailMessage()
    msg.set_content(  # TODO
        "Thank you for requesting a password reset from FEArena.\n\n"
        "It's still a bit primitive here, so we don't have a reset-password link for you, but "
        f"for now you can use this token to change your password: \n\n\t{token}\n\nThank you, "
        "\n-FEArena")
    msg['Subject'] = "FEArena Password Reset"
    msg['From'] = "FEArena"  # TODO
    msg['To'] = email_address
    s = smtplib.SMTP('localhost')
    s.send_message(msg)
    s.quit()
    logging.debug(f"Set password reset token and sent email for user `{username}`")
    return True


def reset_password(username: str, token: str, new_password: str) -> bool:
    """
    Given the correct token, sets the user's password to the given new password.
    Returns True if successful, or False if the token does not exist or has expired.
    If user does not exist, throws ValueError.
    """
    usr = User.objects.get(username=username)
    if not usr:
        logging.info(f"Requested password reset for nonexistent user `{username}` failed")
        raise ValueError("User does not exist")
    # verify token
    token = PasswordResetToken.objects.get(user=usr, token=token)
    if not token:
        logging.info(f"Requested password reset for user `{username}` failed: bad token")
        return False
    if token.expiry <= datetime.datetime.now():
        logging.debug(f"Requested password reset for user `{username}` failed: expired token")
        return False
    # reset password
    usr.set_password(new_password + PEPPER)
    usr.save()
    # delete token
    token.delete()


def change_password(username: str, password: str, new_password: str) -> bool:
    """
    Changes the user's password. Returns True if the change is successful, or
    False if authentication fails first.
    """
    if authenticate_user(username, password + PEPPER):
        usr = User.objects.get(username=username)
        usr.set_password(new_password + PEPPER)
        return True
    return False
