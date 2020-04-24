from django.db import models

# Create your models here.
class bus:
	def __init__(self,no=None,lat=None,lon=None):
		self.no=no
		self.lat=lat
		self.long=lon
