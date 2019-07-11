import datetime
from django.db import models
from users import models as user_models


# Create your models here.

class LeaveType(models.Model):
    type = models.CharField(max_length=255, default='Annual Leave')

    def __str__(self):
        return self.type


class Leave(models.Model):
    user = models.ForeignKey(user_models.LmsUser, on_delete=models.CASCADE)
    type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    from_date = models.DateField(default=datetime.date.today)
    to_date = models.DateField(default=datetime.date.today)
    reason = models.TextField(max_length=1200, default='Not Feeling Well')
