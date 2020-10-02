"""bustrack URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from mapview import views 
urlpatterns = [
	path('',include('mapview.urls')),
    path('reports/', include('reports.urls')),
    path('admin/', admin.site.urls),
    path('login',views.dse),
    path('emp', views.emp),
    path('add',views.add),
    path('empbus', views.empbus),
    path('addBus',views.addBus),
    path('show',views.show,name='show'),
    path('showbus',views.showbus,name='showbus'),
    path('empalerts', views.empalerts),
    path('addalerts',views.addalerts),
    path('showalerts',views.showalerts,name='showAlert'),
    path('editalerts/<int:id>', views.editalerts),
    path('updatealerts/<int:id>', views.updatealerts),  
    path('destroyalerts/<int:id>', views.destroyalerts),  
    path('edit/<int:id>', views.edit),  
    path('update/<int:id>', views.update),  
    path('delete/<int:id>', views.destroy),
    path('editbus/<int:id>', views.editbus),  
    path('updatebus/<int:id>', views.updatebus),
    path('destroybus/<int:id>', views.destroybus), 
    path('empUser', views.empUser),
    path('addUser',views.addUser),
    path('showuser',views.showUser,name='showUser'),
    path('editUser/<int:id>', views.editUser),  
    path('updateUser/<int:id>', views.updateUser),  
    path('deleteUser/<int:id>', views.destroyUser),
    #path('ds.html',),
    # path('empSos', views.empSos),
    # path('addSos',views.addSos), 
    # path('showsos',views.showSos,name='showSOS'),
    # path('editSos/<int:id>', views.editSos),  
    # path('updateSos/<int:id>', views.updateSos),  
    # path('deleteSos/<int:id>', views.destroySos), 
]
