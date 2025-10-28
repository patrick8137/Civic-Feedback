from django.urls import path
from . import views

urlpatterns = [
    path('submit/', views.submit_feedback),
    path('list/', views.get_feedback),
    path('stats/', views.stats),
    path('update-status/<int:feedback_id>/', views.update_status),
]