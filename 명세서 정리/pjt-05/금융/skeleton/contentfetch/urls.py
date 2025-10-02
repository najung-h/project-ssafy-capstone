from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.stock_finder,name='stock_finder'),
    path('delete_comment/', views.delete_comment, name='delete_comment'),
]
