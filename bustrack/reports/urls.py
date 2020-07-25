from django.urls import path
from . import views
urlpatterns = [
    path('',views.reports ,name = 'All-Reports'),
    path('deviceuptime', views.deviceuptime, name='deviceuptime'),
    path('alerts', views.alerts, name='repalerts'),
    path('fleetsummary', views.fleetsummary, name = 'fleetsummary'),
    path('fleetreports', views.fleetreports, name='fleetreports'),
    path('distance',views.distance,name='distance'),
    path('routes',views.routes,name="routes")
]