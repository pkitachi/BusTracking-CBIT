from django.shortcuts import render
from django.http import Http404 
from django.http import HttpResponse,JsonResponse
from . models import Loc
import requests


# url='http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/routes'
# urlt='http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/tracking'
# busses=requests.get(url).json()
# track=requests.get(urlt).json()
r = requests.post('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/login',data={'username':'admin','password':'admin@123'})
p= r.json()['access_token']
td=requests.get('http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/routes',headers={'Authorization':f'Bearer {p}'})
busses=td.json()
track=[]

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
    track=requests.get(urlt).json()
    return HttpResponse(track)
