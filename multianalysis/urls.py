# urls.py for the saas_analyzer app
from django.urls import path
from . import views

app_name = 'saas_analyzer'

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name = "dashboard"),
    path('analyze/', views.analyze_saas, name='analyze_saas'), #New project here
    path('results/', views.view_results, name='results'), #List of projects
    path('results/<slug:slug>/', views.view_results, name='results_with_file'),
    path('download/<slug:slug>/', views.download_results, name='download_results'),
    path('status/', views.analysis_status, name='analysis_status'),
]

# Add to your project's main urls.py:
# path('saas-analyzer/', include('saas_analyzer.urls', namespace='saas_analyzer')),