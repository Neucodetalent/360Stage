from django.urls import path
from . import views

urlpatterns = [
    path('admin1_compose_email/', views.admin1_compose_email, name='admin1_compose_email'),
    path('fetch-client/', views.fetch_client, name='fetch_client'),
    path('get-projects-by-client/<str:client_name>/', views.get_projects_by_client, name='get_projects_by_client'),
    #path('get-open-inprogress-data/', views.get_open_inprogress_data, name='get_open_inprogress_data'),
    
    path('get-seekers-and-statuses/', views.get_seekers_and_statuses, name='get_seekers_and_statuses'),
    path('get-filtered-data/', views.get_filtered_data, name='get_filtered_data'),
    path('fetch-emails/', views.fetch_emails, name='fetch_emails'),
    
    path('insert-link/', views.insert_link, name='insert_link'),
    path('compose-email/', views.compose_email, name='compose_email'),

     # Other routes
    # path('error/', views.error_page, name='error_page'),

    path('admin2_generate_reports/', views.admin2_generate_reports, name='admin2_generate_reports'),
    path('fetch-client-fromview/', views.fetch_client_fromview, name='fetch_client_fromview'),
    path('get-projects-by-client-fromview/<str:client_name>/', views.get_projects_by_client_fromview, name='get_projects_by_client_fromview'),
    path('report-generation-table-fromview/', views.report_generation_table_fromview, name='report_generation_table_fromview'),
    path('run-generate-reports/', views.run_generate_reports, name='run_generate_reports'),

    path('admin3_dashboard/', views.admin3_dashboard, name='admin3_dashboard'),
    path('overall-dashboard-header/', views.overall_dashboard_header, name='overall_dashboard_header'),
    path('filtered-dashboard-header/', views.filtered_dashboard_header, name='filtered_dashboard_header'),
    path('get-filtered-data-fromview/', views.get_filtered_data_fromview, name='get_filtered_data_fromview'),


    path('send_sse_message/', views.send_sse_message, name='send_sse_message'),
    #path('sse_stream/', views.sse_stream, name='sse_stream'),
]   