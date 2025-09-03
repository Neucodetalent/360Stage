from django.urls import path
from . import views

#app_name = 'App_User'
urlpatterns = [
    path('user1_instructions/', views.user1_instructions, name='user1_instructions'),
    path('user2_provider/', views.user2_provider, name='user2_provider'),
    path('user3_seeking/', views.user3_seeking, name='user3_seeking'),
    #path('user4_mcq_questions/<int:seeker_id>/', views.user4_mcq_questions, name='user4_mcq_questions'),
    path('user4_mcq_questions/', views.user4_mcq_questions, name='user4_mcq_questions'),
    #path('user5_written_questions/<int:seeker_id>/', views.user5_written_questions, name='user5_written_questions'),
    path('user5_written_questions/', views.user5_written_questions, name='user5_written_questions'),
]
    

