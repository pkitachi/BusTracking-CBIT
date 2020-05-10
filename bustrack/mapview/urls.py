from django.contrib import admin
from django.urls import path,include,re_path
from . import views

urlpatterns = [
	path('home/',views.index,name='index'),
    #/home/Bus-67/
    re_path(r'^home/Bus-(?P<bno>[0-9]+)/$', views.detail, name='detail'),
    #/home/alerts
    path('home/alerts/',views.alerts,name='alerts'),
    #home/ajax-refresh/
    path('home/ajax-refresh/', views.apicall,name='apicall'),
	#/info/<bno>
    path('info/<bno>/',views.info,name='info'),
    #/home/geofence
    #path('home/geofence',views.geofence,name='alerts'),
	#/home/trackhistory
	path('home/trackhistory',views.trackhistory,name='trackhistory'),
    #/home/replaytracking
	path('home/replaytracking',views.replaytracking,name='replaytracking'),
    #/home/clusterview
	path('home/clusterview',views.clusterview,name='clusterview'),
	#/home/clusterinfo
	path('home/clusterinfo',views.clusterinfo,name='clusterinfo'),
	#home/track-refresh/
	path('home/track-refresh/', views.trackapicall,name='trackapicall'),
]
