from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
import json
import os
from django.conf import settings

# Import the MultiStepSaaSAnalyzer
from services.utils import MultiStepSaaSAnalyzer
from .models import *

def index(request):
    """
    Render the main page with the SaaS analyzer form
    """
    return render(request, 'multianalysis/index.html')

def dashboard(request):
    """
    Dashboard view for SaaS Analyzer
    """
    projects = Project.objects.filter(user=request.user).order_by('-updated_at')[:4]
    
    # Get recent activities
    activities = Project.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    # Get recent projects for sidebar
    recent_projects = Project.objects.filter(user=request.user).order_by('-updated_at')[:5]
    
    # Get statistics
    total_projects = Project.objects.filter(user=request.user).count()
    active_projects = Project.objects.filter(user=request.user, status= False).count()
    # total_reports = Report.objects.filter(project__user=request.user).count()
    
    context = {
        'projects': projects,
        'activities': activities,
        'recent_projects': recent_projects,
        'total_projects': total_projects,
        'active_projects': active_projects,
        # 'total_reports': total_reports,
    }
    
    return render(request, 'multianalysis/dashboard.html', context)


def analyze_saas(request):
    return render(request, 'multianalysis/step_analysis.html')

@csrf_exempt
@require_http_methods(["POST"])
def analyze_step(request):
    """
    Handle step-by-step analysis requests
    """
    try:
        data = json.loads(request.body)
        step = data.get('step')
        saas_name = data.get('saas_name')
        saas_url = data.get('saas_url', None)
        
        # Get any stored analyzer from session or create new
        analyzer_data = request.session.get('analyzer_data', None)
        analyzer = MultiStepSaaSAnalyzer()
        
        # Populate analyzer with previous data if available
        if analyzer_data:
            analyzer.target_saas = analyzer_data.get('target_saas', analyzer.target_saas)
            analyzer.competitors = analyzer_data.get('competitors', analyzer.competitors)
            analyzer.competitor_pain_points = analyzer_data.get('competitor_pain_points', analyzer.competitor_pain_points)
            analyzer.combined_pain_points = analyzer_data.get('combined_pain_points', analyzer.combined_pain_points)
            analyzer.micro_saas_ideas = analyzer_data.get('micro_saas_ideas', analyzer.micro_saas_ideas)
        
        result = None
        
        # Execute the appropriate step
        if step == 'step1':
            result = analyzer.analyze_target_saas(saas_name, saas_url)
        elif step == 'step2':
            result = analyzer.identify_competitors()
        elif step == 'step3':
            result = analyzer.analyze_competitor_pain_points()
        elif step == 'step4':
            # Market gap returned here
            result = analyzer.combine_pain_points()
        elif step == 'step5':
            max_ideas = int(data.get('max_ideas', 3))
            result = analyzer.generate_micro_saas_ideas(max_ideas)
        elif step == 'save':
            result = analyzer.save_analysis()
            request.session['last_analysis_file'] = result
        else:
            return JsonResponse({'error': 'Invalid step'}, status=400)
        
        # Store current analyzer state in session
        analyzer_data = {
            'target_saas': analyzer.target_saas,
            'competitors': analyzer.competitors,
            'competitor_pain_points': analyzer.competitor_pain_points,
            'combined_pain_points': analyzer.combined_pain_points,
            'micro_saas_ideas': analyzer.micro_saas_ideas
        }
        request.session['analyzer_data'] = analyzer_data
        
        return JsonResponse({
            'status': 'success',
            'step': step,
            'result': result
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def view_results(request, filename=None):
    """
    View the analysis results from a saved JSON file
    """
    try:
        if not filename:
            filename = request.session.get('last_analysis_file')
            if not filename:
                messages.error(request, "No analysis results found")
                return redirect('saas_analyzer:index')
        
        # Construct the full path to the JSON file
        file_path = os.path.join(settings.MEDIA_ROOT, filename)
        
        # Check if the file exists
        if not os.path.exists(file_path):
            messages.error(request, f"Analysis file {filename} not found")
            return redirect('saas_analyzer:index')
        
        # Read the analysis data
        with open(file_path, 'r', encoding='utf-8') as f:
            analysis_data = json.load(f)
        
        # Render the template with the analysis data
        return render(request, 'multianalysis/results.html', {
            'analysis': analysis_data,
            'filename': filename
        })
        
    except Exception as e:
        messages.error(request, f"Error viewing results: {str(e)}")
        return redirect('saas_analyzer:dashboard')

def download_results(request, filename=None):
    """
    Download the analysis results as a JSON file
    """
    try:
        if not filename:
            filename = request.session.get('last_analysis_file')
            if not filename:
                messages.error(request, "No analysis results found")
                return redirect('multianalysis:index')
        
        # Construct the full path to the JSON file
        file_path = os.path.join(settings.MEDIA_ROOT, filename)
        
        # Check if the file exists
        if not os.path.exists(file_path):
            messages.error(request, f"Analysis file {filename} not found")
            return redirect('multianalysis:index')
        
        # Read the file and serve it as a download
        with open(file_path, 'r', encoding='utf-8') as f:
            response = HttpResponse(f.read(), content_type='application/json')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        
    except Exception as e:
        messages.error(request, f"Error downloading results: {str(e)}")
        return redirect('multianalysis:index')

def analysis_status(request):
    """
    API endpoint to check the status of an ongoing analysis
    """
    # This would be implemented with a task queue like Celery
    # For now, we'll just return a placeholder
    return JsonResponse({
        'status': 'in_progress',
        'progress': 75,
        'current_step': 'Generating micro-SaaS ideas'
    })