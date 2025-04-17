from django.urls import path
from . import views
from .views import employee_login

urlpatterns = [
    path('login/', employee_login, name='employee_login'),
    path('add/', views.add_user, name='add_user'),
    path('delete/', views.delete_user, name='delete_user'),

]
