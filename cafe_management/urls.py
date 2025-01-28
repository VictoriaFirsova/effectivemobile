
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('orders.urls', namespace='orders')),
    path('api/', include('api.urls')),
]
