from django.urls import path
from app.views import *

urlpatterns = [
    path('', index, name="index"), 
    path('pricing', pricing, name="pricing") ,
    path('dashboard/', dashboard, name='dashboard'),
    path("analysis/api", analysis_api, name="analysis_api"), 
    path('analysis/<slug:slug>/', analysis_detail, name='analysis_detail'),
    path('analysis/<slug:slug>/export/', analysis_export, name='analysis_export'),
    # path('analysis/<slug:slug>/delete/', analysis_delete, name='analysis_delete'),

]

