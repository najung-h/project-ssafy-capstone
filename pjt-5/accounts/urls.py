from django.urls import path
from .views import signup, SignInView, SignOutView, watchlist, add_watch, remove_watch

app_name = 'accounts'
urlpatterns = [
    path('signup/', signup, name='signup'),
    path('login/',  SignInView.as_view(),  name='login'),
    path('logout/', SignOutView.as_view(), name='logout'),

    path('watchlist/', watchlist, name='watchlist'),
    path('watchlist/add/', add_watch, name='add_watch'),
    path('watchlist/<int:pk>/remove/', remove_watch, name='remove_watch'),
]
