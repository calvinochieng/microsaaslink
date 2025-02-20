from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.http import HttpResponseBadRequest
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required



from django.shortcuts import render
from analysis.analyzer import gen
import json
from django.views.decorators.http import require_http_methods
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
import re


from .forms import *
from .models import *

saas_data = [
        {
            "name": "PhotoAI",
            "url": "https://photoai.com",
            "category": "AI Imaging",
            "description": "AI-powered platform for generating photorealistic images and videos from selfies.",
            "pain_point_score": 5,
            "key_pain_points": [
                "Complex interface for new users",
                "Limited customization options",
                "High processing times for large batches"
            ]
        },
        {
            "name": "Jasper AI",
            "url": "https://www.jasper.ai",
            "category": "AI Writing",
            "description": "AI-driven copywriting tool for generating marketing and content materials.",
            "pain_point_score": 3,
            "key_pain_points": [
                "Inconsistent content quality",
                "Limited tone control",
                "Integration challenges"
            ]
        },
        {
            "name": "Synthesia",
            "url": "https://www.synthesia.io",
            "category": "AI Video",
            "description": "Create AI-powered video content with synthetic avatars and voiceovers.",
            "pain_point_score": 4,
            "key_pain_points": [
                "Limited language support",
                "Challenging avatar customization",
                "High video rendering times"
            ]
        },
        {
            "name": "Copy.ai",
            "url": "https://www.copy.ai",
            "category": "Content Creation",
            "description": "AI-powered copywriting tool for generating creative marketing content.",
            "pain_point_score": 3,
            "key_pain_points": [
                "Repetitive content suggestions",
                "Limited industry templates",
                "Lack of advanced integrations"
            ]
        },
        {
            "name": "Gamma",
            "url": "https://gamma.app",
            "category": "Presentations",
            "description": "Interactive presentation tool for creating dynamic and engaging slides.",
            "pain_point_score": 4,
            "key_pain_points": [
                "Steep learning curve",
                "Limited advanced design features",
                "Performance lags with complex slides"
            ]
        },
        {
            "name": "Descript",
            "url": "https://www.descript.com",
            "category": "Audio/Video",
            "description": "All-in-one tool for audio and video editing with AI-powered transcription.",
            "pain_point_score": 4,
            "key_pain_points": [
                "Occasional transcription inaccuracies",
                "High resource usage",
                "Limited advanced editing features"
            ]
        },
        {
            "name": "Loom",
            "url": "https://www.loom.com",
            "category": "Video Messaging",
            "description": "Video messaging tool for instant communication and screen recording.",
            "pain_point_score": 2,
            "key_pain_points": [
                "Basic editing capabilities",
                "Occasional syncing issues",
                "Limited recording customization"
            ]
        },
        {
            "name": "Notion",
            "url": "https://www.notion.so",
            "category": "Productivity",
            "description": "All-in-one workspace for notes, docs, and project management.",
            "pain_point_score": 3,
            "key_pain_points": [
                "Steep learning curve",
                "Limited offline functionality",
                "Performance issues with large datasets"
            ]
        },
        {
            "name": "Figma",
            "url": "https://www.figma.com",
            "category": "Design",
            "description": "Collaborative interface design tool for modern digital products.",
            "pain_point_score": 2,
            "key_pain_points": [
                "Slow collaboration features",
                "Limited offline support",
                "Occasional UI inconsistencies"
            ]
        }
    ]

def index(request):
    
    context = {
        'saas_data': saas_data
    }
    
    return render(request, 'index.html', context)

def pricing(request):
    return render(request, 'pricing.html')

@login_required
def dashboard(request):
    context = {
        'saas_data': None
    }
    return render(request, 'dashboard/dashboard.html', context)


@require_http_methods(["GET", "POST"])
def analysis(request):
    context = {
        'form_errors': {},
        'analysis_data': None
    }
    
    if request.method == "POST":
        # Get form data
        name = request.POST.get('name', '').strip()
        url = request.POST.get('url', '').strip()
        description = request.POST.get('description', '').strip()
        
        # Validate inputs
        if not name:
            context['form_errors']['name'] = 'Product name is required'
        
        if not url:
            context['form_errors']['url'] = 'Product URL is required'
        else:
            # Validate URL format
            url_validator = URLValidator()
            try:
                # Add http:// if not present for validation
                if not url.startswith(('http://', 'https://')):
                    url = 'http://' + url
                url_validator(url)
            except ValidationError:
                context['form_errors']['url'] = 'Please enter a valid URL'
        
        # If no errors, proceed with analysis
        if not context['form_errors']:
            try:
                # Get analysis results
                result = gen(name, url)
                
                # Debug print
                print("Raw result:", result)
                
                # Clean and parse the JSON
                try:
                    # Method 1: Extract JSON string if wrapped in code blocks
                    if "```json" in result:
                        # Extract content between ```json and ```
                        json_str = re.search(r'```json\n(.*?)\n```', result, re.DOTALL)
                        if json_str:
                            result = json_str.group(1)
                    elif "```" in result:
                        # Extract content between ``` and ```
                        json_str = re.search(r'```\n(.*?)\n```', result, re.DOTALL)
                        if json_str:
                            result = json_str.group(1)
                    
                    # Method 2: Clean the string
                    result = result.strip()
                    if result.startswith('`') and result.endswith('`'):
                        result = result[1:-1]
                    
                    # Parse JSON
                    analysis_data = json.loads(result)
                    print("Parsed data:", analysis_data)  # Debug print
                    context['analysis_data'] = analysis_data
                    
                except json.JSONDecodeError as e:
                    print("JSON Decode Error:", str(e))  # Debug print
                    print("Attempted to parse:", result)  # Debug print
                    context['error_message'] = f'Error processing analysis results: {str(e)}'
                    
            except Exception as e:
                print("General Error:", str(e))  # Debug print
                context['error_message'] = f'Error performing analysis: {str(e)}'
        
        # Add form data back to context for form repopulation
        context.update({
            'name': name,
            'url': url,
            'description': description
        })
    
    return render(request, 'dashboard/analysis.html', context)

