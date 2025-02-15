from django.urls import path
from app.views import *

urlpatterns = [
    path('', index, name="index"), 
    path('pricing', pricing, name="pricing") ,
    path('dashboard/', dashboard, name='dashboard'),
    path("analysis", analysis, name="analysis")
]

