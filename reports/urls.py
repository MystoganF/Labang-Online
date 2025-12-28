from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.report_records, name='report_records'),
    path('file/', views.file_report, name='file_report'),
    path('detail/<str:report_id>/', views.report_detail, name='report_detail'),
]