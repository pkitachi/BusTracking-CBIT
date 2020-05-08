from django.shortcuts import render
from django.http import Http404 
from django.http import HttpResponse,JsonResponse
from . models import Loc
import requests
import ast 
from django.conf import settings

# url='http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/routes'
# urlt='http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/tracking'
# busses=requests.get(url).json()
# track=requests.get(urlt).json()
r = requests.post('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/login',data={'username':'admin','password':'admin@123'})
p= r.json()['access_token']
td=requests.get('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/routes',headers={'Authorization':f'Bearer {p}'})
busses=td.json()
#busses=[{'Id':4,'status':'WORKING','IMEI':'120654'},{'Id':5,'status':'WORKING','IMEI':'65842'},{'Id':6,'status':'WORKING','IMEI':'763425'},{'Id':7,'status':'WORKING','IMEI':'7845642321'}]
track=[{'IMEI':'120654','alert':None},{'IMEI':'65842','alert':None},{'IMEI':'763425','alert':None},{'IMEI':'7845642321','alert':1}]
alertRes=[]

def homepage(request):
	locs=Loc.objects.all()

	return render(request,'homepage.html',{"locs":locs,'busses': busses}) 
	
def index(request):
	locs=Loc.objects.all()
	return render(request,'index.html',{"locs":locs,'busses': busses}) 	

def trackhistory(request):
	if request.method=="POST":
		bno=int(request.POST.get('busno'))
		date=request.POST.get('date')
		temp=date.split('-')
		temp[0],temp[2]=temp[2],temp[0]
		date=('-'.join(temp))
		th=requests.get('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/tracking',headers={'Authorization':f'Bearer {p}'},data={'rouoteId':bno,'deviceTime':'2020-05-01'})
		track_his=th.json()
		runHrs=th.json()[-1]['runHrs']
		return render(request,'trackhistory.html',{'runHrs':runHrs,'busses':busses,"bno":bno,"date":date,"track_his":track_his}) 

def detail(request, bno):
	
	locs=Loc.objects.all()
	r = requests.post('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/login',data={'username':'admin','password':'admin@123'})
	p= r.json()['access_token']
	td=requests.get('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/tracking',headers={'Authorization':f'Bearer {p}'},data={'routeId':bno})
	curRaw={'lat':td.json()[0]['latitude'],'lon':td.json()[0]['longitude']}
	prop={'speed':td.json()[0]['speed'],'battery':td.json()[0]['battery'],'fuel':td.json()[0]['fuel']};
	#for i in track:
	#    if(i['Id']==int(bno)):
	#        return render(request, 'bus-detail.html', { 'bus' : i ,'locs' : locs , 'busses': busses})
	# raise Http404("Bus does not exist")
	return render(request, 'bus-detail.html', {'locs' : locs ,'curRaw':curRaw, 'busses': busses,'bno':bno,'prop':prop})

def info(request,bno):
	r = requests.post('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/login',data={'username':'admin','password':'admin@123'})
	p= r.json()['access_token']
	td=requests.get('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/tracking',headers={'Authorization':f'Bearer {p}'},data={'routeId':bno})
	curRaw=td.json()[0]
	
	return JsonResponse(curRaw)

def alerts(request):
	locs=Loc.objects.all()

	return render(request,'alerts.html',{"locs":locs , 'track':track, 'busses': busses}) 

def apicall(request):
    # urlt='http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/tracking'
    track=[{'IMEI':'120654','alert':1},{'IMEI':'65842','alert':1},{'IMEI':'763425','alert':1},{'IMEI':'7845642321','alert':1}]
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
