from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
import json
import re
from django.conf import settings
from django.contrib.auth.decorators import login_required
from datetime import timedelta
from django.utils import timezone
from django.contrib import messages


# Import the MultiStepSaaSAnalyzer
from services.utils import MultiStepSaaSAnalyzer
from .models import *

def index(request):
    """
    Render the main page with the SaaS analyzer form
    """
    return render(request, 'multianalysis/index.html')


@login_required
def dashboard(request):
    """
    Dashboard view for SaaS Analyzer.
    Displays user projects and extra statistics:
      - Total Projects (with % change from last month)
      - Active Analyses (with count of new ones this week)
      - Generated Ideas (with count of new ideas this month)
      - Pain Points Identified (with a note on growth)
    """
    # Retrieve all projects for the logged-in user
    user_projects = Project.objects.filter(user=request.user)
    
    # Main dashboard items
    projects = user_projects.order_by('-updated_at')[:6]
    activities = user_projects.order_by('-created_at')[:5]
    recent_projects = user_projects.order_by('-updated_at')[:5]
    
    # Statistics: total and active projects
    total_projects = user_projects.count()
    active_projects = user_projects.filter(status=False).count()
    
    # Date boundaries
    now = timezone.now()
    start_of_week = now - timedelta(days=now.weekday())  # Monday of current week
    start_of_month = now.replace(day=1)
    
    # New projects from last month: using created_at filtering on previous calendar month
    if now.month == 1:
        last_month = 12
        last_month_year = now.year - 1
    else:
        last_month = now.month - 1
        last_month_year = now.year
    new_projects_last_month = Project.objects.filter(
        user=request.user, 
        created_at__year=last_month_year, 
        created_at__month=last_month
    ).count()
    
    # New projects this week (active analyses that started this week)
    new_projects_this_week = user_projects.filter(created_at__gte=start_of_week).count()
    
    # Aggregated Generated Ideas: sum of lengths of micro_saas_ideas (assuming each is a list)
    generated_ideas = sum(len(p.micro_saas_ideas) if p.micro_saas_ideas else 0 for p in user_projects)
    
    # New ideas this month: for projects updated since the start of this month,
    # count ideas for those projects (this is one way to approximate "new ideas")
    projects_this_month = user_projects.filter(updated_at__gte=start_of_month)
    new_ideas_this_month = sum(len(p.micro_saas_ideas) if p.micro_saas_ideas else 0 for p in projects_this_month)
    
    # Aggregated Pain Points Identified across projects:
    pain_points = 0
    for project in user_projects:
        # Count pain points from the target SaaS analysis
        if project.target_saas and isinstance(project.target_saas, dict):
            pain_points += len(project.target_saas.get('pain_points', []))
        # Count pain points from competitor analyses
        if project.competitor_pain_points and isinstance(project.competitor_pain_points, dict):
            for pain_list in project.competitor_pain_points.values():
                pain_points += len(pain_list)
    
    # For demonstration, use a placeholder for percentage change from last month.
    # You might compute this from historical data.
    project_change_percentage = "25%"  # Example placeholder
    
    context = {
        'projects': projects,
        'activities': activities,
        'recent_projects': recent_projects,
        'total_projects': total_projects,
        'active_projects': active_projects,
        'project_change_percentage': project_change_percentage,  # e.g., "25% from last month"
        'new_projects_last_month': new_projects_last_month,        # could be shown alongside total projects
        'new_projects_this_week': new_projects_this_week,          # e.g., "2 new this week"
        'generated_ideas': generated_ideas,
        'new_ideas_this_month': new_ideas_this_month,              # e.g., "12 new this month"
        'pain_points_identified': pain_points,                     # e.g., "87 Growing database"
    }
    
    return render(request, 'multianalysis/dashboard/dashboard.html', context)

@login_required
def analyze_saas(request):
    user_input = request.GET.get('input', '').strip()  # Get input and strip spaces

    if not user_input:
        messages.error(request, "No input provided. Please enter a name or a website link.")
    # Regex pattern to match only domain-based URLs (excluding IPs and localhost)
    url_pattern = re.compile(
        r'^(?:http|https)://'  # Match URLs starting with http:// or https://
        r'([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'  # Match domains like example.com
        r'(?:[/?#]\S*)?$',  # Allow query parameters, paths, etc.
        re.IGNORECASE
    )

    if re.match(url_pattern, user_input):
        url = user_input if user_input.startswith(('http://', 'https://')) else f'http://{user_input}'
        name = ''
    else:
        name = user_input
        url = ''

    context = {
        'name': name,
        'url': url
    }
    return render(request, 'multianalysis/step_analysis.html', context)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def analyze_step(request):
    """
    Handle step-by-step analysis requests.
    """
    try:
        data = json.loads(request.body)
        print(data)
        step = data.get('step')
        saas_name = data.get('saas_name')
        saas_url = data.get('saas_url', None)
        
        # Add a "new_project" flag to explicitly create a new project
        create_new = data.get('new_project', False)
        
        # Get project_id from session
        project_id = request.session.get('project_id')
        print("Session project_id:", project_id)
        
        # Create a new project if requested or if no project exists
        if create_new or not project_id:
            project = Project.objects.create(
                user=request.user,
                name=saas_name if saas_name else "Untitled Project",
                url=saas_url
            )
            request.session['project_id'] = project.id
            project_id = project.id
        else:
            try:
                # Check if the project exists and belongs to the current user
                project = Project.objects.get(id=project_id, user=request.user)
            except Project.DoesNotExist:
                # If project doesn't exist or doesn't belong to user, create a new one
                project = Project.objects.create(
                    user=request.user,
                    name=saas_name if saas_name else "Untitled Project",
                    url=saas_url
                )
                request.session['project_id'] = project.id
                project_id = project.id
        
        # Retrieve any stored analyzer state from the session
        analyzer_data = request.session.get('analyzer_data', None)
        
        # Instantiate the analyzer with the project instance, not just the id.
        analyzer = MultiStepSaaSAnalyzer(project_id=project_id)
        
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
            # If we're starting step 1, we should reset the analyzer data
            analyzer_data = {
                'target_saas': analyzer.target_saas,
                'competitors': [],
                'competitor_pain_points': [],
                'combined_pain_points': [],
                'micro_saas_ideas': []
            }
        elif step == 'step2':
            result = analyzer.identify_competitors()
        elif step == 'step3':
            result = analyzer.analyze_competitor_pain_points()
        elif step == 'step4':
            result = analyzer.combine_pain_points()
        elif step == 'step5':
            max_ideas = int(data.get('max_ideas', 3))
            result = analyzer.generate_micro_saas_ideas(max_ideas)
        elif step == 'save':
            result = analyzer.save_analysis()
            request.session['last_analysis_file'] = result
            # Clear the project_id from session after saving
            if 'project_id' in request.session:
                del request.session['project_id']
            if 'analyzer_data' in request.session:
                del request.session['analyzer_data']
        else:
            return JsonResponse({'error': 'Invalid step'}, status=400)
        
        # Store current analyzer state in the session
        if step != 'save':  # Don't update analyzer data if we just saved
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
            'result': result,
            'slug': project.slug,
            'project_id': project_id  # Return the project ID in the response
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def save_project(request):
    return JsonResponse({'status': 'success', 'message': 'Analysis saved successfully'})

@login_required
def view_project(request, slug):
    """
    View analysis results based on the Project's slug.
    """
    try:
        # Retrieve the project by slug, ensuring it belongs to the logged-in user.
        project = get_object_or_404(Project, slug=slug, user=request.user)
        
        # Prepare the analysis data from the Project instance.
        analysis_data = {
            'target_saas': project.target_saas,
            'competitors': project.competitors,
            'competitor_pain_points': project.competitor_pain_points,
            'combined_pain_points': project.combined_pain_points,
            'micro_saas_ideas': project.micro_saas_ideas,
            'created_at': project.created_at,
            'updated_at': project.updated_at,
        }
        
        # Render the template with the analysis data.
        return render(request, 'multianalysis/result.html', {
            'analysis': analysis_data,
            'project': project
        })
        
    except Exception as e:
        messages.error(request, f"Error viewing results: {str(e)}")
        return redirect('saas_analyzer:dashboard')

@login_required
def view_projects(request):
    items = Project.objects.filter(user=request.user).order_by('-updated_at')
    context = {
        'items': items
    }
    return render(request, 'multianalysis/projects.html', context)

@login_required
def active_projects(request):
    items = Project.objects.filter(user=request.user, status=False)
    context = {
        'items': items
    }
    return render(request, 'multianalysis/projects.html', context)

@login_required
def micro_saas_ideas(request):
    # Get all projects for the current user
    projects = Project.objects.filter(user=request.user)
    ideas = []
    
    # Iterate over each project and aggregate micro SaaS ideas
    for project in projects:
        # Each project has a JSON field `micro_saas_ideas` that is a list of ideas
        for idea in project.micro_saas_ideas:
            # Optionally attach the project name to each idea for context
            idea['project_name'] = project.name
            ideas.append(idea)
    
    context = {
        'items': ideas  # This list now contains all micro SaaS ideas from the user's projects
    }
    
    return render(request, 'multianalysis/micro_saas_ideas.html', context)
