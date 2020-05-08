from django.shortcuts import render
from django.http import Http404 
from django.http import HttpResponse,JsonResponse
from . models import Loc
import requests


# url='http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/routes'
# urlt='http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/tracking'
# busses=requests.get(url).json()
# track=requests.get(urlt).json()
# r = requests.post('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/login',data={'username':'admin','password':'admin@123'})
# p= r.json()['access_token']
# td=requests.get('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/routes',headers={'Authorization':f'Bearer {p}'})
# busses=td.json()
busses=[{'Id':4,'status':'WORKING','IMEI':'120654'},{'Id':5,'status':'WORKING','IMEI':'65842'},{'Id':6,'status':'WORKING','IMEI':'763425'},{'Id':7,'status':'WORKING','IMEI':'7845642321'}]
track=[{'IMEI':'120654','alert':None},{'IMEI':'65842','alert':None},{'IMEI':'763425','alert':None},{'IMEI':'7845642321','alert':1}]
alertRes=[]

def homepage(request):
	locs=Loc.objects.all()

	return render(request,'homepage.html',{"locs":locs,'busses': busses}) 
def index(request):
	locs=Loc.objects.all()
	return render(request,'index.html',{"locs":locs,'busses': busses}) 	

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
    urlt='http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/tracking'
    track=[{'IMEI':'120654','alert':1},{'IMEI':'65842','alert':None},{'IMEI':'763425','alert':None},{'IMEI':'7845642321','alert':1}]
    flag=0
    for i in track:
        if i['alert']==1:
            if len(alertRes)==0:
                dictr = dict()
                dictr['IMEI'] = i['IMEI']
                dictr['new'] = 1
                alertRes.append(dictr)
            else:
                for j in alertRes:
                    if i['IMEI'] == j['IMEI']:
                        j['new'] = 0
                        flag=1
                        break
                if flag==0:
                    dictr = dict()
                    dictr['IMEI'] = i['IMEI']
                    dictr['new'] = 1
                    alertRes.append(dictr)
    return JsonResponse(alertRes,safe=False)