from django.db import models
from django.contrib.auth.models import User


class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField()
    expiry = models.DateTimeField()



