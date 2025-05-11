from django.urls import path
from . import views

urlpatterns = [
    path('submit/', views.submit_suggestion_or_complaint, name='submit_suggestion_or_complaint'),
    path('track/<int:complaint_id>/', views.track_complaint, name='track_complaint'),
    path('detail/<int:complaint_id>/', views.retrive_complaint_by_id, name='retrive_complaint_by_id'),
    path('complaints/', views.get_complaints, name='get_complaints'),
    path('update-status/<int:complaint_id>/', views.update_complaint_status, name='update_complaint_status'),
    path('delete/<int:complaint_id>/', views.delete_complaint, name='delete_complaint'),
    path('statistics/', views.get_complaint_statistics, name='get_complaint_statistics'),
    path('statistics/', views.get_complaint_statistics, name='get_complaint_statistics'),
    path('trends/', views.get_complaint_trends, name='get_complaint_trends'),
    path('generate-report/', views.generate_report, name='generate_report'),
    path('delete-report/<int:report_id>/', views.delete_report, name='delete_report'),
    path('get-report/<int:report_id>/', views.get_report_by_id, name='get_report_by_id'),
    path('list-reports/', views.list_all_reports, name='list_all_reports'),


]
