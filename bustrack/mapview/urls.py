from django.contrib import admin
from django.urls import path,include,re_path
from . import views

urlpatterns = [
    #/
    path('',views.login,name='login'),
    #/signup
    path('signup',views.signup,name='signup'),
    #/forgotpwd
    path('forgot-password',views.forgotpwd,name='forgotpwd'),
    #/logout
    path('logout',views.logout,name='logout'),
    #/home/
	path('home/',views.index,name='index'),
    #/home/Bus-67/
    re_path(r'^home/Bus-(?P<bno>[0-9]+)/$', views.detail, name='detail'),
    #/home/alerts
    path('home/alerts/',views.alerts,name='alerts'),
    #home/ajax-refresh/
    path('home/ajax-refresh/', views.apicall,name='apicall'),
    #home/alert-call/
    re_path(r'^home/alert-call/(?P<date>.+)/$', views.alertcall,name='alertcall'),
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
    #/home/buses
    path('home/buses',views.buses,name='buses'),
	#home/track-refresh/
	path('home/track-refresh/', views.trackapicall,name='trackapicall'),
	path('home/geofence',views.geofence,name='geofence'),
	path('home/add_geofence', views.add_geofence, name='add_geofence'),
    path('home/view_geofence', views.view_geofence, name='view_geofence'),
	#Reports_Section
    path('home/reports/deviceuptime', views.r_deviceuptime, name='deviceuptime'),
	path('home/reports/geofence_report',views.geofence_report,name='geofence_report'),
    path('home/reports/alerts', views.r_alerts, name='r_alerts'),
    path('home/reports/fleetsummary', views.r_fleetsummary, name = 'fleetsummary'),
    path('home/reports/speedviolation', views.r_speedviolation, name='speedviolation'),
    path('home/reports/distance',views.r_distance,name='distance'),
    path('home/reports/routes',views.r_routes,name="routes")
	
]
