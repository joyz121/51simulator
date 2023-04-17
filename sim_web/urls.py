from django.urls import path,include
from django.contrib import admin
import notifications.urls
from login import views
from . import sim
urlpatterns = [
    path('sim/',sim.run),
    path('admin/',admin.site.urls),
    path('login/',views.login),
    path('register/',views.register),
    path('logout/',views.logout),
    path('notifications/',include(notifications.urls,namespace='notifications')),
    path('my_notifications/',views.my_notifications,name='my_notifications'),
]
