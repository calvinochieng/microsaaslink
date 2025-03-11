# admin.py (optional - if you want to manage results in the admin)
from django.contrib import admin
from .models import *

# @admin.register(AnalysisResult)
# class AnalysisResultAdmin(admin.ModelAdmin):
#     list_display = ('target_saas_name', 'created_at', 'is_complete')
#     search_fields = ('target_saas_name',)
#     list_filter = ('is_complete', 'created_at')
