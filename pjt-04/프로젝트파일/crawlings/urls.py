# crawlings/urls.py

from django.urls import path
from . import views

app_name = 'crawlings'

urlpatterns = [
    path('', views.index, name="index"),
    path('index/',views.index),
    # 1) 크롤링 전용 (DB 저장만 하고 끝나면, 출력으로 redirect)
    path('comments/crawl/', views.comments_crawling, name='comments_crawling'),
    # 2) 출력 전용
    path('comments/', views.comments_printing, name='comments_printing'),
    # 3) 삭제 → 출력으로 redirect
    path('comments/<int:pk>/delete/', views.delete, name='delete'),
]
