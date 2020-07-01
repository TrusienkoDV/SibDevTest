from django.db import models

# Create your models here.


class Deal(models.Model):
    customer = models.TextField()
    item = models.TextField()
    total = models.IntegerField()
    quantity = models.IntegerField()
    date = models.DateTimeField()
