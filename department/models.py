from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Department(models.Model):
    department = models.CharField(max_length=500, default='Administration', unique=True)
    head_of_department = models.ForeignKey(User, on_delete=models.CASCADE,
                                           related_name='head_of_department', default=1)

    def __str__(self):
        return self.department


class Notice(models.Model):
    topic = models.CharField(max_length=100, default="Emergency Notice", null=False, blank=False)
    message = models.TextField(null=False, blank=False)

    def __str__(self):
        return self.topic