from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Department(models.Model):
    department = models.CharField(max_length=500, default='Administration', unique=True)
    head_of_department = models.ForeignKey(User, on_delete=models.CASCADE,
                                           related_name='head_of_department', default=1)

    def __str__(self):
        return self.department
