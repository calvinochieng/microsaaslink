from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.http import HttpResponseBadRequest, JsonResponse

from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from analysis.analyzer import gen
import json
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
    # Get analyses for the current user only, ordered by newest first
    saas_data = SaaSAnalysis.objects.filter(
        user=request.user
    ).order_by('-created_at')
    
    context = {
        'saas_data': saas_data
    }
    return render(request, 'dashboard/dashboard.html', context)



@login_required
def analysis_detail(request, slug):
    analysis = get_object_or_404(SaaSAnalysis, slug=slug, user=request.user)
    context = {
        'analysis_data': analysis.analysis_result,
        'has_data': bool(analysis.analysis_result)
    }
    return render(request, 'dashboard/analysis_detail.html', context)

@login_required
def analysis_export(request, slug):
    analysis = get_object_or_404(SaaSAnalysis, slug=slug, user=request.user)
    # Your export logic here




@login_required
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
                    # print("Parsed data:", analysis_data)  # Debug print
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



@login_required
def analysis_api(request):
    if request.method != "POST":
        return JsonResponse({"message": "Method not allowed"}, status=405)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON in request body."}, status=400)
    
    name = data.get('name', '').strip()
    url = data.get('url', '').strip()
    
    form_errors = {}
    
    if not name:
        form_errors['name'] = 'Product name is required'
    
    if not url:
        form_errors['url'] = 'Product URL is required'
    else:
        url_validator = URLValidator()
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'http://' + url
            url_validator(url)
        except ValidationError:
            form_errors['url'] = 'Please enter a valid URL'
    
    if form_errors:
        return JsonResponse({"form_errors": form_errors}, status=400)
    
    try:
        response_data = gen(name, url)
    
        saas_data_json = response_data['saas_data_json']
        search_queries = response_data['search_queries']
        token_info = response_data['token_info']
        # print(saas_data_json)
        description = saas_data_json.get('saas_product', {}).get('description', '')
        # print(description)

        # Save analysis result
        analysis = SaaSAnalysis.objects.create(
            user=request.user,
            product_url=url,
            product_name=name,
            search_queries = search_queries,
            description=description,
            analysis_result=saas_data_json
        )
        
        return JsonResponse({ 
            "slug": analysis.slug,
            "result": saas_data_json
        }, status=201) 
        
    except json.JSONDecodeError as e:
        return JsonResponse({
            "error": f"Error processing analysis results: {str(e)}",
            "raw_result": result if isinstance(result, str) else str(result)
        }, status=500)
    except Exception as e:
        return JsonResponse({
            "error": f"Error performing analysis: {str(e)}"
        }, status=500)