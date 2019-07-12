import datetime
from django.db import models
from lms_user import models as user_models


# Create your models here.

class LeaveQuerySet(models.QuerySet):
    def get_monthly_leave_detail(self, user, month):
        return self.filter(
            models.Q(user=user) & (models.Q(from_date__month=month) | models.Q(to_date__month=month)) & models.Q(
                leave_approved=True) & models.Q(leave_pending=False)
        )


class LeaveType(models.Model):
    type = models.CharField(max_length=255, default='Annual Leave')

    def __str__(self):
        return self.type


class Leave(models.Model):
    user = models.ForeignKey(user_models.LmsUser, on_delete=models.CASCADE)
    type = models.ForeignKey(LeaveType, on_delete=models.SET_DEFAULT, default=1)
    from_date = models.DateField(default=datetime.date.today)
    to_date = models.DateField(default=datetime.date.today)
    half_day = models.BooleanField(default=False)
    reason = models.TextField(max_length=1200, default='Not Feeling Well')
    leave_pending = models.BooleanField(default=True)
    leave_approved = models.BooleanField(default=False)
    notification = models.BooleanField(default=True)# true = should be notify #false = should not notify
    objects = LeaveQuerySet.as_manager()

    def __str__(self):
        return '{} - {}'.format(self.user, self.type)


class Holiday(models.Model):
    title = models.CharField(max_length=1200, blank=False)
    from_date = models.DateField(null=False,blank=False,default=datetime.date.today)
    to_date = models.DateField(null=False,blank=False,default=datetime.date.today)
    description = models.TextField(max_length=1200, blank=False)
    image = models.FileField(upload_to='lms_user/static/lms_user/site-data/holidays', blank=True)

    def __str__(self):
        return '{}'.format(self.title)

    def delete(self, *args, **kwargs):
        self.image.delete()
        super().delete(*args,**kwargs)


class CompensationLeave(models.Model):
    user = models.ForeignKey(user_models.LmsUser, on_delete=models.CASCADE)
    days = models.IntegerField(null=False,blank=False,default=0)
    reason = models.TextField(max_length=1200, default="Over time last week")
    leave_pending = models.BooleanField(default=True)
    leave_approved = models.BooleanField(default=False)
    notification = models.BooleanField(default=True)# true = should be notify #false = should not notify

    def __str__(self):
        return f'{self.user}'

