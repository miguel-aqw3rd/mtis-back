from django.urls import path
from mtisAapp import endpoints

urlpatterns = [
    path('signup', endpoints.signup),
    path('login', endpoints.login),
    path('logout', endpoints.logout),
    path('name', endpoints.change_name),
]