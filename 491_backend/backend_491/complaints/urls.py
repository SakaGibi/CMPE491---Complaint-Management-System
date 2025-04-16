from django.urls import path
from . import views

urlpatterns = [
    path('submit/', views.submit_suggestion_or_complaint, name='submit_suggestion_or_complaint'),
    path('track/<int:complaint_id>/', views.track_complaint, name='track_complaint'),

]
