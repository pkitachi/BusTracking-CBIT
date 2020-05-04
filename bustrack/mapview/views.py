from django.shortcuts import render
from django.http import Http404 
from django.http import HttpResponse
from . models import Loc
import requests

url='http://ec2-3-7-131-60.ap-south-1.compute.amazonaws.com/routes'
busses=requests.get(url).json()

def homepage(request):
	locs=Loc.objects.all()

	return render(request,'homepage.html',{"locs":locs,  'busses': busses}) 
def index(request):
	locs=Loc.objects.all()
	return render(request,'index.html',{"locs":locs, 'busses': busses}) 	

def detail(request, bno):
    
    locs=Loc.objects.all()
    for i in busses:
        if(i['routeId']==int(bno)):
            return render(request, 'bus-detail.html', { 'bus' : i, 'locs' : locs , 'busses': busses})
    raise Http404("Bus does not exist")
    return render(request, 'bus-detail.html', {'locs' : locs , 'busses': busses})

def alerts(request):
	locs=Loc.objects.all()

	return render(request,'alerts.html',{"locs":locs ,  'busses': busses}) 
