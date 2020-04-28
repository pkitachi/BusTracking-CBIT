from django.shortcuts import render
from django.http import HttpResponse
from . models import Loc

def homepage(request):
	locs=Loc.objects.all()

	return render(request,'homepage.html',{"locs":locs}) 
def index(request):
	locs=Loc.objects.all()

	return render(request,'index.html',{"locs":locs}) 	
