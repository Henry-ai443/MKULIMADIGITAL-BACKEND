
from django.contrib import admin
from django.urls import path, include

from django.http import HttpResponse

def home():
    return  HttpResponse("THIS IS THE DEFAULT HOMEPAGE FOR THE MKULIMA DIGITAL API")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('users.urls')),
    path('', home, name="home"),
]
