from django.contrib import admin
from django.urls import path, include
from contentfetch import views
from django.views.generic.base import RedirectView


urlpatterns = [
    path('pjt05/admin/', admin.site.urls),
    path('pjt05/', include('contentfetch.urls')),
]
