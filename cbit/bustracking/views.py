from django.shortcuts import render
from django.shortcuts import render
from django.http import HttpResponse
import pymysql
from . models import bus
# Create your views here.
def homepage(request):
	db=pymysql.connect("localhost","root","","bustracking")
	cursor=db.cursor()
	cs=[]
	cursor.execute("select id,latitude,longitude from buslatlong;")
	lst=cursor.fetchall()
	for i in range(len(lst)):
		#no=int(i[1:3])
		#lat=float(i[5:12])
		#lon=float(i[13:-2])
		#no=int(lst[0][1:-1])
		#lat=float(lst[1][1:-1])
		#lon=float(lst[2][1:-1])

		cs.append(bus(lst[i][0],lst[i][1],lst[i][2]))

	return render(request,'homepage.html',{"comps":cs})