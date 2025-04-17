from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_csv, name='upload_csv'),
    path('report/', views.show_report, name='show_report'),
    path('download/', views.download_report, name='download_report'),
]
