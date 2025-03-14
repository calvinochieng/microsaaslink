# urls.py for the saas_analyzer app
from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('privacy-policy/', privacy_policy, name='privacy_policy'),
    path("refund-policy/", refund_policy, name="refund_policy"),
    path('terms-of-services/', terms_of_service, name='terms_of_service'),
    path('saas-list/', saas_list, name='saas_list'),   
    path('pricing', pricing, name="pricing") ,
    path('dashboard/', dashboard, name = "dashboard"),
    path('analyze/', analyze_saas, name='analyze_saas'), #New project here
    path('analyze-step/', analyze_step, name ='analyze_step'),
    path("save-project/", save_project, name="save_project"),
    path('projects/', view_projects, name='projects'), #List of projects
    path('active-projects/', active_projects, name='active_projects'), #List of active projects
    path('micro-saas-ideas/', micro_saas_ideas, name='micro_saas_ideas'), #List of micro saas ideas
    path('project/<slug:slug>/', view_project, name='project_detail'),
]

# Add to your project's main urls.py:
# path('saas-analyzer/', include('saas_analyzer.urls', namespace='saas_analyzer')),