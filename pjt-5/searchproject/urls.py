# searchproject / urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    # root만 사용하고 namespace는 여기 한 군데에만 부여
    path('', include(('crawlings.urls', 'crawlings'), namespace='crawlings')),
    # /crawlings/로 들어오면 root로 리다이렉트 (선택)
    path('crawlings/', RedirectView.as_view(pattern_name='crawlings:index', permanent=False)),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
]
