
from django.contrib import admin
from django.urls import path, include

from django.http import JsonResponse

def home(request):
    return JsonResponse({'Message':"The default mkulima digital home api"})
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('users.urls')),
    path('', home, name="home"),
]
