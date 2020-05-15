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
from pytz import timezone
from django.views.decorators.csrf import csrf_exempt
import json

r = requests.post('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/login',data={'username':'admin','password':'admin@123'})
p= r.json()['access_token']
alertRes=[]

def login(request):
	
	return render(request,'login.html') 
def signup(request):
	
	return render(request,'register.html') 
def forgotpwd(request):

	return render(request,'forgot-password.html') 
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

def inBusGeofence(lat,lng,lats_lngs):
	lat = float(lat)
	lng = float(lng)
	lats_lngs = [ (float(i[0]),float(i[1])) for i in lats_lngs]
	polygon = Polygon(lats_lngs) 
	point = Point(lng,lat) 
	if point.within(polygon):
		return True
	return False 

bus_in_status = {}
bus_indi_status = {}
bus_res = None

def geofence_check():
	threading.Timer(10.0, geofence_check).start()
	track=requests.get('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/tracking',headers={'Authorization':f'Bearer {p}'})
	tr = track.json()

	# get api request for individual geofence
	bus_geofence_response = requests.get('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/busgeofence',headers={'Authorization':f'Bearer {p}'})
	bus_res = bus_geofence_response.json()

	for i in tr:

		# check if bus is in its geofence
		routeIds = str(i['routeId'])
		if(bus_res.get(routeIds) != None):
			check_res = inBusGeofence(i['latitude'],i['longitude'],bus_res[routeIds])
			if(not check_res and bus_indi_status.get(routeIds) != None and bus_indi_status.get(routeIds)):

				# if bus moves out of geofence.. raise alert
				print("Should Raise Alert Here")
			bus_indi_status[routeIds] = check_res

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
	t=requests.get('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/routes',headers={'Authorization':f'Bearer {p}'})
	buses=t.json()
	runHrs=None;bno=None;date=None;track_his=None;driver={};
	if request.method=="POST":
		bno=int(request.POST.get('busno'))
		date=request.POST.get('date')
		temp=date.split('-')
		temp[0],temp[2]=temp[2],temp[0]
		date=('-'.join(temp))
		th=requests.get('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/tracking',headers={'Authorization':f'Bearer {p}'},data={'routeId':bno,'deviceTime':date})
		track_his=th.json()
		try:
			runHrs=th.json()[-1]['runHrs']
			dname=th.json()[0]['driverName']
			dphone=th.json()[0]['driverPhone']
		except IndexError:
			return render(request,'indexerror.html')
	return render(request,'trackhistory.html',{'runHrs':runHrs,'buses':buses,"bno":bno,"date":date,"track_his":track_his,"dname":dname,"dphone":dphone})

def replaytracking(request):
	t=requests.get('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/routes',headers={'Authorization':f'Bearer {p}'})
	buses=t.json()
	if request.method=="POST":
		bno=int(request.POST.get('bno'))
		date=request.POST.get('ddate')
		temp=date.split('-')
		temp[0],temp[2]=temp[2],temp[0]
		date=('-'.join(temp))
		th=requests.get('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/tracking',headers={'Authorization':f'Bearer {p}'},data={'routeId':bno,'deviceTime':date})
		track_replay=th.json()
		runHrs=th.json()[-1]['runHrs']
		dname=th.json()[0]['driverName']
		dphone=th.json()[0]['driverPhone']
		return render(request,'replayTrack.html',{'runHrs':runHrs,'buses':buses,"bno":bno,"date":date,"track_replay":track_replay,"dname":dname,"dphone":dphone}) 

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
	t=requests.get('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/routes',headers={'Authorization':f'Bearer {p}'})
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
	tr=requests.get('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/tracking',headers={'Authorization':f'Bearer {p}'})
	track=tr.json()
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
		gDate=request.POST.get('date1')
		gDate1=request.POST.get('date2')
		dir=int(request.POST.get('dir'))
		temp=gDate.split('-')
		temp[0],temp[2]=temp[2],temp[0]
		gDate=('-'.join(temp))
		temp1=gDate1.split('-')
		temp1[0],temp1[2]=temp1[2],temp1[0]
		gDate1=('-'.join(temp1))
		if request.POST['busno']:
			if dir>=0:
				ress=requests.get('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/geofence',headers={'Authorization':f'Bearer {p}'},data={'routeId':bno,'fromDate':gDate,'toDate':gDate1,'status':dir})
			else:
				ress=requests.get('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/geofence',headers={'Authorization':f'Bearer {p}'},data={'routeId':bno,'fromDate':gDate,'toDate':gDate1})
		else:
			if dir>=0:
				ress=requests.get('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/geofence',headers={'Authorization':f'Bearer {p}'},data={'fromDate':gDate,'toDate':gDate1,'status':dir})
			else:
				ress=requests.get('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/geofence',headers={'Authorization':f'Bearer {p}'},data={'fromDate':gDate,'toDate':gDate1})
		geofence_report=ress.json()
	return render(request,'geofence_report.html',{'cluster':cluster,'buses': buses,'geofence_report':geofence_report})

		
def buses(request):
	b = requests.get('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/routes',headers={'Authorization':f'Bearer {p}'})
	b = b.json()
	return render(request,'buses.html',{'buses':b}) 

def geofence(request):
	td=requests.get('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/tracking',headers={'Authorization':f'Bearer {p}'})
	tracking=td.json()
	rt=requests.get('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/routes',headers={'Authorization':f'Bearer {p}'})
	buses=rt.json()
	return render(request,'geofence.html',{'buses':buses,'tracking':tracking})

@csrf_exempt
def add_geofence(request):
	b1=requests.get('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/routes',headers={'Authorization':f'Bearer {p}'})
	buses=b1.json()
	if request.method == "POST":
		busnum = request.POST.get('busno')
		if 'polyarray' in request.POST:
			polyarray = request.POST['polyarray']
			busno = request.POST['bno']
			obj = eval(polyarray)
			pno = 1
			requests.delete('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/busgeofence',headers={'Authorization':f'Bearer {p}'},json={'routeId': busno})
			for i in obj:
				print(i)
				requests.post('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/busgeofence',headers={'Authorization':f'Bearer {p}'},json={'routeId': busno,'latitude':i[0],'longitude':i[1],'pointNum':pno})
				pno += 1
	return render(request, 'add_geofence.html', {'buses':buses,'busnum': busnum})

@csrf_exempt
def view_geofence(request):
	bs=requests.get('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/routes',headers={'Authorization':f'Bearer {p}'})
	buses=bs.json()
	busnum = None
	td=requests.get('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/busgeofence',headers={'Authorization':f'Bearer {p}'})
	bus_res=td.json()
	if request.method == "POST":
		busnum = request.POST.get('busno')
	bus_res = [ {'lat':float(i[1]),'lng':float(i[0])} for i in bus_res[busnum]]
	return render(request,'bus_geofence.html',{'buses':buses,'bus_co':bus_res,'busnum':busnum})
