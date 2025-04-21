from django.urls import path
from . import views

urlpatterns = [
    path('submit/', views.submit_support_message, name='submit_support_message'),
    path('faq/', views.get_faq, name='get_faq'),
    path('delete/<int:message_id>/', views.delete_support_message, name='delete_support_message'),
    path('answer/<int:message_id>/', views.answer_support_message, name='answer_support_message'),
    path('list/', views.get_support_requests, name='get_support_requests'),

]