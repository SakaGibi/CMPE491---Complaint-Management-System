from django.urls import path
from . import views
from .views import employee_login

urlpatterns = [
    path('login/', employee_login, name='employee_login'),
    path('add/', views.add_user, name='add_user'),
    path('delete/', views.delete_user, name='delete_user'),
    path('list/', views.get_user_list, name='get_user_list'),
    path('change-role/', views.change_user_role, name='change_user_role'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),

]
