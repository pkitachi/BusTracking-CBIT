from django.db import models

# Create your models here.
class Loc(models.Model):
	bno = models.IntegerField()
	lat = models.DecimalField(max_digits=9, decimal_places=6)
	lon = models.DecimalField(max_digits=9, decimal_places=6)