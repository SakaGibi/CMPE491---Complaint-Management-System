from django.urls import path
from . import views

urlpatterns = [
    path('submit/', views.submit_support_message, name='submit_support_message'),
]