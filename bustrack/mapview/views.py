from django.shortcuts import render
from django.http import Http404 
from django.http import HttpResponse,JsonResponse
from . models import Loc
import requests
import ast 
from django.conf import settings
import threading
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import numpy as np
from datetime import datetime,date

r = requests.post('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/login',data={'username':'admin','password':'admin@123'})
p= r.json()['access_token']
alertRes=[]

def inGeofence(lat,lng):
	lat = float(lat)
	lng = float(lng)
	lons_lats_vect = [(78.321499,17.392993),(78.319181,17.394380),(78.318103,17.393592),(78.317213,17.389937),(78.320316,17.389174)]
	polygon = Polygon(lons_lats_vect) 
	point = Point(lng,lat) 
	#polygon.contains(point)
	if point.within(polygon):
		return 1
	return 0 

bus_in_status = {}

def geofence_check():
	threading.Timer(10.0, geofence_check).start()
	track=requests.get('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/tracking',headers={'Authorization':f'Bearer {p}'})
	tr = track.json()
	for i in tr:
		if (bus_in_status.get(i['IMEI']) == None) or (bus_in_status.get(i['IMEI']) != inGeofence(i['latitude'],i['longitude'])):	
			res = inGeofence(i['latitude'],i['longitude'])
			gDate = str(date.today())
			gTime = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
			if(bus_in_status.get(i['IMEI']) != None):
				requests.post('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/geofence',headers={'Authorization':f'Bearer {p}'},json={'IMEI': i['IMEI'],'gDate':gDate,'gTime':gTime,'status':res})
			# post into api inGeofence(i['latitude'],i['longitude'])
			bus_in_status[i['IMEI']] = res
			# bus_in_status[i['IMEI']] = api result
geofence_check()      


def trackapicall(request):
	th=requests.get('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/tracking',headers={'Authorization':f'Bearer {p}'})
	track_liv=th.json()
	return JsonResponse(track_liv,safe=False)	
	
def index(request):
	t=requests.get('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/routes',headers={'Authorization':f'Bearer {p}'})
	buses=t.json()
	td=requests.get('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/tracking',headers={'Authorization':f'Bearer {p}'},data={'routeId':None,'deviceTime':None})
	track_liv=td.json()
	return render(request,'index.html',{'buses':buses,'track_liv':track_liv}) 

def trackhistory(request):
	t=requests.get('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/buses',headers={'Authorization':f'Bearer {p}'})
	buses=t.json()
	if request.method=="POST":
		bno=int(request.POST.get('busno'))
		date=request.POST.get('date')
		temp=date.split('-')
		temp[0],temp[2]=temp[2],temp[0]
		date=('-'.join(temp))
		th=requests.get('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/tracking',headers={'Authorization':f'Bearer {p}'},data={'routeId':bno,'deviceTime':date})
		track_his=th.json()
		runHrs=th.json()[-1]['runHrs']
		return render(request,'trackhistory.html',{'runHrs':runHrs,'buses':buses,"bno":bno,"date":date,"track_his":track_his})

def replaytracking(request):
	t=requests.get('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/buses',headers={'Authorization':f'Bearer {p}'})
	buses=t.json()
	if request.method=="POST":
		bno=int(request.POST.get('bno'))
		date=request.POST.get('ddate')
		temp=date.split('-')
		temp[0],temp[2]=temp[2],temp[0]
		date=('-'.join(temp))
		th=requests.get('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/tracking',headers={'Authorization':f'Bearer {p}'},data={'routeId':bno,'deviceTime':date})
		track_his=th.json()
		runHrs=th.json()[-1]['runHrs']
		return render(request,'replayTrack.html',{'runHrs':runHrs,'buses':buses,"bno":bno,"date":date,"track_his":track_his}) 

def clusterview(request):
	t=requests.get('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/buses',headers={'Authorization':f'Bearer {p}'})
	buses=t.json()
	t=requests.get('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/tracking',headers={'Authorization':f'Bearer {p}'})
	cluster=t.json()
	return render(request,'clusterview.html',{'cluster':cluster,'buses': buses})
	
def clusterinfo(request):
	trk=requests.get('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/tracking',headers={'Authorization':f'Bearer {p}'})
	return JsonResponse(trk.json(),safe=False)

def detail(request, bno):
	t=requests.get('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/buses',headers={'Authorization':f'Bearer {p}'})
	buses=t.json()
	td=requests.get('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/tracking',headers={'Authorization':f'Bearer {p}'},data={'routeId':bno})
	curRaw={'lat':td.json()[0]['latitude'],'lon':td.json()[0]['longitude']}
	prop={'speed':td.json()[0]['speed'],'battery':td.json()[0]['battery'],'fuel':td.json()[0]['fuel']}
	return render(request, 'bus-detail.html', {'curRaw':curRaw, 'buses': buses,'bno':bno,'prop':prop})

def info(request,bno):
	td=requests.get('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/tracking',headers={'Authorization':f'Bearer {p}'},data={'routeId':bno})
	curRaw=td.json()[0]
	
	return JsonResponse(curRaw)

def alerts(request):
	t=requests.get('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/buses',headers={'Authorization':f'Bearer {p}'})
	buses=t.json()
	return render(request,'alerts.html',{'track':track, 'buses': buses}) 

def apicall(request):
    tr=requests.get('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/tracking',headers={'Authorization':f'Bearer {p}'})
    track=tr.json()
    alertRes = []
    for i in track:
        if i['alert']==1:
            if i not in alertRes:
                alertRes.append(i)
    return JsonResponse(alertRes,safe=False)

def geofence_report(request):
	track_data=requests.get('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/tracking',headers={'Authorization':f'Bearer {p}'})
	cluster=track_data.json()
	bus = requests.get('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/routes',headers={'Authorization':f'Bearer {p}'})
	buses = bus.json()
	geofence_report = None
	if request.method=="POST":
		bno=request.POST.get('busno')
		gDate=request.POST.get('date')
		temp=gDate.split('-')
		temp[0],temp[2]=temp[2],temp[0]
		gDate=('-'.join(temp))
		if(bno==''):
			ress=requests.get('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/geofence',headers={'Authorization':f'Bearer {p}'},data={'gDate':gDate})
		else:
			ress=requests.get('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/geofence',headers={'Authorization':f'Bearer {p}'},data={'routeId':bno,'gDate':gDate})
			geofence_report=ress.json()
	return render(request,'geofence_report.html',{'cluster':cluster,'buses': buses,'geofence_report':geofence_report})

		
def buses(request):
	b = requests.get('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/routes',headers={'Authorization':f'Bearer {p}'})
	b = b.json()
	return render(request,'buses.html',{'buses':b}) 

def geofence(request):
	td=requests.get('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/tracking',headers={'Authorization':f'Bearer {p}'})
	tracking=td.json()
	return render(request,'geofence.html',{'tracking':tracking})
