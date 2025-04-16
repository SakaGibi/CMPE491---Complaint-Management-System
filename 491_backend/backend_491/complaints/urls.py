from django.urls import path
from . import views

urlpatterns = [
    path('submit/', views.submit_suggestion_or_complaint, name='submit_suggestion_or_complaint'),
    path('track/<int:complaint_id>/', views.track_complaint, name='track_complaint'),
    path('detail/<int:complaint_id>/', views.retrive_complaint_by_id, name='retrive_complaint_by_id'),
    path('complaints/', views.get_complaints, name='get_complaints'),

]
