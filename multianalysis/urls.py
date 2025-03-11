# urls.py for the saas_analyzer app
from django.urls import path
from . import views

app_name = 'saas_analyzer'

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name = "dashboard"),
    path('analyze/', views.analyze_saas, name='analyze_saas'), #New project here
    path('analyze-step/', views.analyze_step, name ='analyze_step'),
    path('projects/', views.projects, name='projects'), #List of projects
    path('active-projects/', views.active_projects, name='active_projects'), #List of active projects
    path('micro-saas-ideas/', views.micro_saas_ideas, name='micro_saas_ideas'), #List of micro saas ideas
    path('project/<slug:slug>/', views.project, name='project_detail'),
]

# Add to your project's main urls.py:
# path('saas-analyzer/', include('saas_analyzer.urls', namespace='saas_analyzer')),