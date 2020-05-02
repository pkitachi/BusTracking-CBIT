from django.shortcuts import render
from django.http import Http404 
from django.http import HttpResponse
from . models import Loc

def homepage(request):
	locs=Loc.objects.all()

	return render(request,'homepage.html',{"locs":locs}) 
def index(request):
	locs=Loc.objects.all()

	return render(request,'index.html',{"locs":locs}) 	

def detail(request, bno):
    
    locs=Loc.objects.all()
    try:
        bus=Loc.objects.get(bno=bno)
    except Loc.DoesNotExist:
        raise Http404("Bus does not exist")
    return render(request, 'bus-detail.html', { 'bus' : bus, 'locs' : locs })

def alerts(request):
	locs=Loc.objects.all()

	return render(request,'alerts.html',{"locs":locs}) 
