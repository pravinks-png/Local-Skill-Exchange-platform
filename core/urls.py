from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('api/auth/register/', views.api_register, name='api_register'),
    path('api/auth/login/', views.api_login, name='api_login'),
    path('api/skills/', views.api_skills, name='api_skills'),
    path('api/skills/<str:skill_id>/', views.api_skill_detail, name='api_skill_detail'),
    path('api/appointments/', views.api_appointments, name='api_appointments'),
    path('api/appointments/<str:appt_id>/status/', views.api_appointment_status, name='api_appointment_status'),
    path('api/seed/', views.api_seed, name='api_seed'),
]
