from django.db import models
from django.contrib.auth.models import User
from department.models import Department


# Create your models here.

class LmsUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='lms_department',
                                   default=1)
    leave_issuer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leave_issuer')

    def __str__(self):
        return self.user.username
