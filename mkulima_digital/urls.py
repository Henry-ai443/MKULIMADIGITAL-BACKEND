
from django.contrib import admin
from django.urls import path, include

from django.http import JsonResponse

def home(request):
    return JsonResponse({'Message':"The default mkulima digital home api"})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('api/products/', include('products.urls')),
    path('api/orders/', include('orders.urls')),
    path('', home, name="home"),
]
