from django.db import models


# Create your models here.
class RhymeType(models.Model):
    type = models.CharField(max_length=30, default='No Leave Rhyme')

    def __str__(self):
        return self.type


class Rhyme(models.Model):
    title = models.CharField(default='Rhyme', max_length=199)
    rhyme = models.TextField(max_length=1000,
                             default='Twinkle twinkle have you any wool. Twinkle twinkle had a great fall.')
    type = models.ForeignKey(RhymeType, on_delete=models.SET_DEFAULT, default=1)

    def __str__(self):
        return self.title
