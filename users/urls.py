from django.urls import path
from .views import profile, user_login, user_logout, register

app_name = 'users'


urlpatterns = [
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('register/', register, name='register'),
    path('profile/', profile, name='profile'),
]

