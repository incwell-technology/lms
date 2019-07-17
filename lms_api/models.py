import secrets
from django.db import models
from lms_user.models import LmsUser


# Create your models here.

class APIToken(models.Model):
    user = models.OneToOneField(LmsUser, on_delete=models.CASCADE)
    api_key = models.CharField(max_length=86, default=secrets.token_urlsafe, unique=True)

    def __str__(self):
        return self.api_key
