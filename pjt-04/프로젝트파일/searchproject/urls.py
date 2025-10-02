# searchproject / urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('crawlings.urls')),
    path('admin/', admin.site.urls),
    path('crawlings/', include('crawlings.urls')),
]
