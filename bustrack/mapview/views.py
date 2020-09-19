from django.shortcuts import render,redirect
from django.http import Http404 
import smtplib
from django.http import HttpResponseRedirect
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
import datetime as dt
from .prevent import UserLoginRateThrottle



alertRes=[]

r=None
p=None
td=None
def login(request):
	if (request.method)=="POST":
		throttle_classes = UserLoginRateThrottle()
		uname=request.POST['username']
		pas=request.POST['password']
		rme=request.POST['rememberme']
		clientkey=request.POST['g-recaptcha-response']
		secretkey='6Lfts_sUAAAAAK-VYv2g8qDlRZIGclCf1J_XtRE8'
		captchaData={
		'secret':secretkey,
		'response':clientkey
		
		}
		a=requests.post('https://www.google.com/recaptcha/api/siteverify',data=captchaData)
		res=a.json()
		if(res['success']):
			try:
				global r 
				global p
				global td
				r = requests.post('http://ec2-13-233-193-38.ap-south-1.compute.amazonaws.com/login',data={'username':uname,'password':pas})
				p= r.json()['access_token']
				accept,num=throttle_classes.allow_request(uname,1)
				if accept:
					t=requests.get('http://ec2-13-233-193-38.ap-south-1.compute.amazonaws.com/routes',headers={'Authorization':f'Bearer {p}'})
					buses=t.json()
					td=requests.get('http://ec2-13-233-193-38.ap-south-1.compute.amazonaws.com/tracking',headers={'Authorization':f'Bearer {p}'},data={'routeId':None,'deviceTime':None})
					track_liv=td.json()
					return index(request,rme)	
				else:
					s1="user "+uname+" is blocked"
					s={'status':s1}
					return render(request,'login.html',{'data':s})

			except KeyError:
				accept,num=throttle_classes.allow_request(uname,0)
				if accept==True:
					num1=3-(num)
					s={'num':num1,'status':'','user':uname}
					return render(request,'incorrect_login.html',{'data':s})
				else:
					s1="user "+uname+" is blocked"
					s={'status':s1}
					return render(request,'login.html',{'data':s})
			except:
				return render(request,"404.html")
		else:
			s1="Please verify captcha"
			s={'status':s1}
			return render(request,'login.html',{'data':s})

				
	else:
		s={'status':''}
		return render(request,'login.html',{'data':s})

def resp():
	s={'status':'1'}
	return JsonResponse(s,safe=False)
def signup(request):
	if (request.method)=="POST":
		uname=request.POST['username']
		passw=request.POST['password']
		repassw=request.POST['repeatPassword']
		fname=request.POST['firstName']
		lname=request.POST['lastName']
		email=request.POST['email']
		phoneNumber=request.POST['phoneNumber']
		vendorId=request.POST['vendorid']
		if(passw!=repassw):
			return render(request,'invalidsignup.html',{'data':' Both Password fields do not match','color':'danger'})
		r = requests.post('http://ec2-13-233-193-38.ap-south-1.compute.amazonaws.com/register',data={'username':uname,'password':passw,'firstName':fname,'lastName':lname,'phone':phoneNumber,'email':email,'createdDate':date.today(),'updatedDate':date.today(),'vendorId':vendorId})
		if(str(r)=='<Response [201]>'):
			return render(request,'invalidsignup.html',{'data':r.json()['message'],'color':'success'})
		if(str(r)=='<Response [400]>'):
			return render(request,'invalidsignup.html',{'data':'true','color':'danger'})
		return render(request,'invalidsignup.html',{'data':'Error Signing up','color':'danger'})
	return render(request,'register.html') 
def forgotpwd(request):

	return render(request,'forgot-password.html')
def logout(request):
	global p
	p=None
	return redirect('/')

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
	track=requests.get('http://ec2-13-233-193-38.ap-south-1.compute.amazonaws.com/tracking',headers={'Authorization':f'Bearer {p}'})
	tr = track.json()

	# get api request for individual geofen
	global bus_res
	bus_geofence_response = requests.get('http://ec2-13-233-193-38.ap-south-1.compute.amazonaws.com/busgeofence',headers={'Authorization':f'Bearer {p}'})
	bus_res = bus_geofence_response.json()

	for i in tr:
# check if bus is in its geofence
		routeIds = str(i['routeId'])
		t=str(i['updatedTime'])
		format = '%a, %d %b %Y %H:%M:%S GMT' ;ds = str(dt.datetime.strptime(t, format));
		if(bus_res.get(routeIds) != None):
			check_res = inBusGeofence(i['latitude'],i['longitude'],bus_res[routeIds])
			if(not check_res and bus_indi_status.get(routeIds) != None and bus_indi_status.get(routeIds)):

				# if bus moves out of geofence.. raise alert
				print("Should Raise Alert Here")
				outalert = requests.post('http://ec2-13-233-193-38.ap-south-1.compute.amazonaws.com/alerts',headers={'Authorization':f'Bearer {p}','Content-Type':'application/json'},json={'smsStatus':0,'routeId':i['routeId'],'alertDate':str(i['deviceTime']),'alertTime':ds,'alertCode':'100'});
			elif(check_res and bus_indi_status.get(routeIds) !=None and not bus_indi_status.get(routeIds)):
				# bus coming back into the geofence..... raise alert
				print("Should Raise an incoming alert here")
				inalert = requests.post('http://ec2-13-233-193-38.ap-south-1.compute.amazonaws.com/alerts',headers={'Authorization':f'Bearer {p}','Content-Type':'application/json'},json={'smsStatus':0,'routeId':i['routeId'],'alertDate':str(i['deviceTime']),'alertTime':ds,'alertCode':'200'});
			bus_indi_status[routeIds] = check_res

		if (bus_in_status.get(i['IMEI']) == None) or (bus_in_status.get(i['IMEI']) != inGeofence(i['latitude'],i['longitude'])):	
			res = inGeofence(i['latitude'],i['longitude'])
			gDate = str(date.today())
			gTime = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
			if(bus_in_status.get(i['IMEI']) != None):
				requests.post('http://ec2-13-233-193-38.ap-south-1.compute.amazonaws.com/geofence',headers={'Authorization':f'Bearer {p}'},json={'IMEI': i['IMEI'],'gDate':gDate,'gTime':gTime,'status':res})
			# post into api inGeofence(i['latitude'],i['longitude'])
			bus_in_status[i['IMEI']] = res
			# bus_in_status[i['IMEI']] = api result

def trackapicall(request):
	th=requests.get('http://ec2-13-233-193-38.ap-south-1.compute.amazonaws.com/tracking',headers={'Authorization':f'Bearer {p}'})
	track_liv=th.json()
	return JsonResponse(track_liv,safe=False)	
	
def index(request, rme = ''):
	if(p!=None):
		t=requests.get('http://ec2-13-233-193-38.ap-south-1.compute.amazonaws.com/routes',headers={'Authorization':f'Bearer {p}'})
		buses=t.json()
		td=requests.get('http://ec2-13-233-193-38.ap-south-1.compute.amazonaws.com/tracking',headers={'Authorization':f'Bearer {p}'},data={'routeId':None,'deviceTime':None})
		track_liv=td.json()
		tBus=[]
		bBus=[]
		onBus=[]
		offBus=[]
		for i in track_liv:
			tBus.append({'routeId':i['routeId'],'routeName':i['routeName']})
		for i in buses:
			bBus.append({'routeId':i['routeId'],'routeName':i['routeName']})
		for i in bBus:
			if(i in tBus):
				onBus.append(i)
			else:
				offBus.append(i)
		return render(request,'index.html',{'buses':buses,'track_liv':track_liv,'rme':rme,'onBus':onBus,'offBus':offBus})
	else:
		s={'status':''}
		return redirect('/')

def trackhistory(request):
	if(p!=None):
		t=requests.get('http://ec2-13-233-193-38.ap-south-1.compute.amazonaws.com/routes',headers={'Authorization':f'Bearer {p}'})
		buses=t.json()
		runHrs=None;bno=None;date=None;track_his=None;driver={};
		if request.method=="POST":
			bno=int(request.POST.get('busno'))
			date=request.POST.get('date')
			temp=date.split('-')
			temp[0],temp[2]=temp[2],temp[0]
			date=('-'.join(temp))
			th=requests.get('http://ec2-13-233-193-38.ap-south-1.compute.amazonaws.com/tracking',headers={'Authorization':f'Bearer {p}'},data={'routeId':bno,'deviceTime':date})
			track_his=th.json()
			try:
				#runHrs=th.json()[-1]['runHrs']
				dname=th.json()[0]['driverName']
				dphone=th.json()[0]['driverPhone']
				vNo=th.json()[0]['vehicleNo']
			except IndexError:
				return render(request,'indexerror.html',{'buses':buses})#'runHrs':runHrs,
		return render(request,'trackhistory.html',{'vNo':vNo,'buses':buses,"bno":bno,"date":date,"track_his":track_his,"dname":dname,"dphone":dphone})
	else:
		s={'status':''}
		return redirect('/')
		
def eta(request, bno):
	t=requests.get('http://ec2-13-233-193-38.ap-south-1.compute.amazonaws.com/routes',headers={'Authorization':f'Bearer {p}'})
	buses=t.json()
	td=requests.get('http://ec2-13-233-193-38.ap-south-1.compute.amazonaws.com/tracking',headers={'Authorization':f'Bearer {p}'},data={'routeId':bno})
	if(td.json()==[]):
		return render(request, 'busStopsEta.html', {'curRaw':{'lat':0,'lng':0}, 'buses': buses,'bno':bno,'prop':{}})
	curRaw={'lat':td.json()[0]['latitude'],'lon':td.json()[0]['longitude']}
	# prop={'speed':td.json()[0]['speed'],'battery':td.json()[0]['battery_volatge'],'fuel':td.json()[0]['fuel'],}
	global bus_res
	try:
		bus_co = [{'lat': float(i[1]), 'lng': float(i[0])} for i in bus_res[bno]]
	except:
		bus_co=[]
	bStops = requests.get('http://ec2-13-233-193-38.ap-south-1.compute.amazonaws.com/busstops',headers={'Authorization':f'Bearer {p}'},data={'routeId':bno})
	return render(request, 'busStopsEta.html', {'curRaw':curRaw, 'buses': buses,'bno':bno,'prop':td.json()[0],'bus_co':bus_co, 'bStops':bStops.json()})
		
		
def replaytracking(request):
	if(p!=None):
		t=requests.get('http://ec2-13-233-193-38.ap-south-1.compute.amazonaws.com/routes',headers={'Authorization':f'Bearer {p}'})
		buses=t.json()
		if request.method=="POST":
			bno=int(request.POST.get('bno'))
			date=request.POST.get('ddate')
			temp=date.split('-')
			temp[0],temp[2]=temp[2],temp[0]
			date=('-'.join(temp))
			th=requests.get('http://ec2-13-233-193-38.ap-south-1.compute.amazonaws.com/tracking',headers={'Authorization':f'Bearer {p}'},data={'routeId':bno,'deviceTime':date})
			track_replay=th.json()
			#runHrs=th.json()[-1]['runHrs']
			vNo=th.json()[0]['vehicleNo']
			dname=th.json()[0]['driverName']
			dphone=th.json()[0]['driverPhone']#'runHrs':runHrs,
			return render(request,'replayTrack.html',{'vNo':vNo,'buses':buses,"bno":bno,"date":date,"track_replay":track_replay,"dname":dname,"dphone":dphone}) 
	else:
		s={'status':''}
		return redirect('/')
def clusterview(request):
	if(p!=None):
		t=requests.get('http://ec2-13-233-193-38.ap-south-1.compute.amazonaws.com/routes',headers={'Authorization':f'Bearer {p}'})
		buses=t.json()
		t=requests.get('http://ec2-13-233-193-38.ap-south-1.compute.amazonaws.com/tracking',headers={'Authorization':f'Bearer {p}'})
		cluster=t.json()
		return render(request,'clusterview.html',{'cluster':cluster,'buses': buses})
	else:
		s={'status':''}
		return redirect('/')	
def clusterinfo(request):
	trk=requests.get('http://ec2-13-233-193-38.ap-south-1.compute.amazonaws.com/tracking',headers={'Authorization':f'Bearer {p}'})
	return JsonResponse(trk.json(),safe=False)

def detail(request, bno):
	if(p!=None):
		t=requests.get('http://ec2-13-233-193-38.ap-south-1.compute.amazonaws.com/routes',headers={'Authorization':f'Bearer {p}'})
		buses=t.json()
		td=requests.get('http://ec2-13-233-193-38.ap-south-1.compute.amazonaws.com/tracking',headers={'Authorization':f'Bearer {p}'},data={'routeId':bno})
		if(td.json()==[]):
			return render(request, 'bus-detail.html', {'curRaw':{'lat':0,'lng':0}, 'buses': buses,'bno':bno,'prop':{}})
		curRaw={'lat':td.json()[0]['latitude'],'lon':td.json()[0]['longitude']}
		global bus_res
		try:
			bus_co = [{'lat': float(i[1]), 'lng': float(i[0])} for i in bus_res[bno]]
		except:
			bus_co=[]
		return render(request, 'bus-detail.html', {'curRaw':curRaw, 'buses': buses,'bno':bno,'prop':td.json()[0],'bus_co':bus_co})
	else:
		s={'status':''}
		return redirect('/')	
def info(request,bno):
	td=requests.get('http://ec2-13-233-193-38.ap-south-1.compute.amazonaws.com/tracking',headers={'Authorization':f'Bearer {p}'},data={'routeId':bno})
	curRaw=td.json()[0]
	
	return JsonResponse(curRaw)

def alerts(request):
	if(p!=None):
		tr=requests.get('http://ec2-13-233-193-38.ap-south-1.compute.amazonaws.com/tracking',headers={'Authorization':f'Bearer {p}'})
		track=tr.json()
		t=requests.get('http://ec2-13-233-193-38.ap-south-1.compute.amazonaws.com/buses',headers={'Authorization':f'Bearer {p}'})
		buses=t.json()
		if (request.method)=="POST":
			gmailaddress =request.POST['smail']
			gmailpassword=request.POST['pass']
			mailto=request.POST['rmail']
			msg=request.POST['comment']
			mailServer = smtplib.SMTP('smtp.gmail.com' , 587)
			mailServer.starttls()
			mailServer.login(gmailaddress , gmailpassword)
			mailServer.sendmail(gmailaddress, mailto , msg)
			mailServer.quit()
			return HttpResponseRedirect(request.path_info)
		else:
			return render(request,'alerts.html',{'track':track, 'buses': buses})
	else:
		s={'status':''}
		return redirect('/') 
def apicall(request):
	if(p!=None):
		today = date.today()
		datee=str(today.year)+'-'+str(today.month)+'-'+str(today.day)
		tr=requests.get('http://ec2-13-233-193-38.ap-south-1.compute.amazonaws.com/alerts',headers={'Authorization':f'Bearer {p}'},data={'alertDate':datee})
		alertRes=tr.json()
		return JsonResponse(alertRes,safe=False)
	else:
		s={'status':''}
		return redirect('/')
def sms(request,msg):
	global p
	t=requests.post('http://ec2-13-233-193-38.ap-south-1.compute.amazonaws.com/sms',headers={'Authorization':f'Bearer {p}'},data={'to':'krishna','description':msg})
	return None

def alertcall(request, date):
	tr=requests.get('http://ec2-13-233-193-38.ap-south-1.compute.amazonaws.com/alerts',headers={'Authorization':f'Bearer {p}'}, data={'alertDate':date})
	track=tr.json()
	return JsonResponse(track,safe=False)

def geofence_report(request):
	if(p!=None):
		track_data=requests.get('http://ec2-13-233-193-38.ap-south-1.compute.amazonaws.com/tracking',headers={'Authorization':f'Bearer {p}'})
		cluster=track_data.json()
		bus = requests.get('http://ec2-13-233-193-38.ap-south-1.compute.amazonaws.com/routes',headers={'Authorization':f'Bearer {p}'})
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
					ress=requests.get('http://ec2-13-233-193-38.ap-south-1.compute.amazonaws.com/geofence',headers={'Authorization':f'Bearer {p}'},data={'routeId':bno,'fromDate':gDate,'toDate':gDate1,'status':dir})
				else:
					ress=requests.get('http://ec2-13-233-193-38.ap-south-1.compute.amazonaws.com/geofence',headers={'Authorization':f'Bearer {p}'},data={'routeId':bno,'fromDate':gDate,'toDate':gDate1})
			else:
				if dir>=0:
					ress=requests.get('http://ec2-13-233-193-38.ap-south-1.compute.amazonaws.com/geofence',headers={'Authorization':f'Bearer {p}'},data={'fromDate':gDate,'toDate':gDate1,'status':dir})
				else:
					ress=requests.get('http://ec2-13-233-193-38.ap-south-1.compute.amazonaws.com/geofence',headers={'Authorization':f'Bearer {p}'},data={'fromDate':gDate,'toDate':gDate1})
			geofence_report=ress.json()
		return render(request,'geofence_report.html',{'cluster':cluster,'buses': buses,'geofence_report':geofence_report})
	else:
		s={'status':''}
		return redirect('/')
		
def buses(request):
	if(p!=None):
		b = requests.get('http://ec2-13-233-193-38.ap-south-1.compute.amazonaws.com/routes',headers={'Authorization':f'Bearer {p}'})
		b = b.json()
		drv = requests.get('http://ec2-13-233-193-38.ap-south-1.compute.amazonaws.com/sms',headers={'Authorization':f'Bearer {p}'})
		drv = drv.json()
		if (request.method)=="POST":
			lis=request.POST.get('lis')
			message=request.POST['mess']
			l1=list(map(str,lis.strip().split(',')))
			num=[]
			for i in range(len(l1)-1):
				num.append(int(l1[i].replace('Bus - ','')))
			print(num)
			return HttpResponseRedirect(request.path_info)
		else:
			return render(request,'buses.html',{'buses':b}) 
	else:
		s={'status':''}
		return redirect('/')
def geofence(request):
	if(p!=None):
		td=requests.get('http://ec2-13-233-193-38.ap-south-1.compute.amazonaws.com/tracking',headers={'Authorization':f'Bearer {p}'})
		tracking=td.json()
		rt=requests.get('http://ec2-13-233-193-38.ap-south-1.compute.amazonaws.com/routes',headers={'Authorization':f'Bearer {p}'})
		buses=rt.json()
		return render(request,'geofence.html',{'buses':buses,'tracking':tracking})
	else:
		s={'status':''}
		return redirect('/')

def changep(request):
	global p
	uname=request.POST['username']
	pas=request.POST['password']
	r = requests.post('http://ec2-13-233-193-38.ap-south-1.compute.amazonaws.com/login',data={'username':uname,'password':pas})
	p= r.json()['access_token']
	return redirect('index')
@csrf_exempt
def add_geofence(request):
	if(p!=None):
		b1=requests.get('http://ec2-13-233-193-38.ap-south-1.compute.amazonaws.com/routes',headers={'Authorization':f'Bearer {p}'})
		buses=b1.json()
		if request.method == "POST":
			busnum = request.POST.get('busno')
			if 'polyarray' in request.POST:
				polyarray = request.POST['polyarray']
				busno = request.POST['bno']
				obj = eval(polyarray)
				pno = 1
				requests.delete('http://ec2-13-233-193-38.ap-south-1.compute.amazonaws.com/busgeofence',headers={'Authorization':f'Bearer {p}'},json={'routeId': busno})
				for i in obj:
					print(i)
					requests.post('http://ec2-13-233-193-38.ap-south-1.compute.amazonaws.com/busgeofence',headers={'Authorization':f'Bearer {p}'},json={'routeId': busno,'latitude':i[0],'longitude':i[1],'pointNum':pno})
					pno += 1
		return render(request, 'add_geofence.html', {'buses':buses,'busnum': busnum})
	else:
		s={'status':''}
		return redirect('/')

@csrf_exempt
def view_geofence(request):
	if(p!=None):
		bs=requests.get('http://ec2-13-233-193-38.ap-south-1.compute.amazonaws.com/routes',headers={'Authorization':f'Bearer {p}'})
		buses=bs.json()
		busnum = None
		td=requests.get('http://ec2-13-233-193-38.ap-south-1.compute.amazonaws.com/busgeofence',headers={'Authorization':f'Bearer {p}'})
		bus_res=td.json()
		if request.method == "POST":
			busnum = request.POST.get('busno')
		bus_res = [ {'lat':float(i[1]),'lng':float(i[0])} for i in bus_res[busnum]]
		return render(request,'bus_geofence.html',{'buses':buses,'bus_co':bus_res,'busnum':busnum})
	else:
		s={'status':''}
		return redirect('/')