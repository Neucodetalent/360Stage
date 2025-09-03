from django.urls import path
from . import views
#app_name = 'App_Superuser'

urlpatterns = [
    path('superuser1_dashboard/', views.superuser1_dashboard, name='superuser1_dashboard'),
    path('superuser-table-filtered-data/', views.get_filtered_data, name='get_filtered_data'),
    path('superuser-overall-dashboard/', views.overall_dashboard_header, name='overall_dashboard_header'),
    path('superuser_pdf', views.superuser_pdf, name='superuser_pdf'),
    # path('download-dashboard-pdf/', views.download_dashboard_pdf, name='download_dashboard_pdf'),
    # path('export-status-pdf/', views.export_status_pdf, name='export_status_pdf'),  # New URL for PDF export
]
