from django.shortcuts import render
from django.http import Http404 
from django.http import HttpResponse,JsonResponse
from . models import Loc
import requests
import ast 
from django.conf import settings

r = requests.post('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/login',data={'username':'admin','password':'admin@123'})
p= r.json()['access_token']
td=requests.get('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/routes',headers={'Authorization':f'Bearer {p}'})
buses=td.json()
track=requests.get('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/tracking',headers={'Authorization':f'Bearer {p}'})
alertRes=[]

	
def trackapicall(request):
	th=requests.get('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/tracking',headers={'Authorization':f'Bearer {p}'},data={'routeId':None,'deviceTime':None})
	track_liv=th.json()
	return JsonResponse(track_liv,safe=False)	
def index(request):
	td=requests.get('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/tracking',headers={'Authorization':f'Bearer {p}'},data={'routeId':None,'deviceTime':None})
	track_liv=td.json()
	return render(request,'index.html',{'track_liv':track_liv}) 

def trackhistory(request):
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
	t=requests.get('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/tracking',headers={'Authorization':f'Bearer {p}'})
	cluster=t.json()
	return render(request,'clusterview.html',{'cluster':cluster,'buses': buses})
	
def clusterinfo(request):
	trk=requests.get('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/tracking',headers={'Authorization':f'Bearer {p}'})
	return JsonResponse(trk.json(),safe=False)

def detail(request, bno):
	td=requests.get('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/tracking',headers={'Authorization':f'Bearer {p}'},data={'routeId':bno})
	curRaw={'lat':td.json()[0]['latitude'],'lon':td.json()[0]['longitude']}
	prop={'speed':td.json()[0]['speed'],'battery':td.json()[0]['battery'],'fuel':td.json()[0]['fuel']}
	return render(request, 'bus-detail.html', {'curRaw':curRaw, 'buses': buses,'bno':bno,'prop':prop})

def info(request,bno):
	td=requests.get('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/tracking',headers={'Authorization':f'Bearer {p}'},data={'routeId':bno})
	curRaw=td.json()[0]
	
	return JsonResponse(curRaw)

def alerts(request):

	return render(request,'alerts.html',{'track':track, 'buses': buses}) 

def apicall(request):
    track=requests.get('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/tracking',headers={'Authorization':f'Bearer {p}'})
    track=track.json()
    alertRes = []
    for i in track:
        if i['alert']==1:
            if i not in alertRes:
                alertRes.append(i)
    return JsonResponse(alertRes,safe=False)

def geofence(request):

	Out=[{'lat':17.4400,'lng':78.3489,'deviceId':42}
		]
	In=[{'lat':17.4058,'lng':78.4032,'deviceId':42}
		]
	lines = []
	url = settings.STATIC_ROOT +'/mapview/static/geofence/42bus.txt'
	
	with open(url) as file:
		for line in file:
			line = line.rstrip()
			if(len(line)>1):
				line=ast.literal_eval(line)
				lines.append(line)
			
	path=lines
	return render(request,'geofence.html', {"data":In,"path":path } ) 
