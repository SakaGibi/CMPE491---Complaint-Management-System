from django.urls import path
from . import views

urlpatterns = [
    path('submit/', views.submit_suggestion_or_complaint, name='submit_suggestion_or_complaint'),
]
