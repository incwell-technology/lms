from django.db import models
from department.models import Department
from django.contrib.auth.models import User
from django.utils import timezone


# Create your models here.

class LmsUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user')
    department = models.ForeignKey(Department, on_delete=models.SET_DEFAULT, related_name='lms_department',
                                   default=1)
    image = models.FileField(upload_to='lms_user/static/lms_user/site-data/profile-pictures', blank=True)
    leave_issuer = models.ForeignKey(User, on_delete=models.SET_DEFAULT, related_name='leave_issuer',
                                     default=1)
    date_of_birth = models.DateField(default=timezone.now)
    joined_date = models.DateField(default=timezone.now)
    phone_number = models.CharField(max_length=15, blank=True)
    sick_leave = models.FloatField(default=7)
    annual_leave = models.FloatField(default=12)
    compensation_leave = models.FloatField(default=0)
    fcm_token = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return '{} {}'.format(self.user.first_name, self.user.last_name)
