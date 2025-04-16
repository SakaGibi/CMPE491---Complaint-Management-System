from django.urls import path
from .views import employee_login

urlpatterns = [
    path('login/', employee_login, name='employee_login'),
]
