from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.http import HttpResponseBadRequest
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from analysis import analyzer

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

def analysis(request):
  
    name = "Render"
    url = "render.com"
    description = ""
    input = f"""
            INPUT:
            - SaaS Product Name/URL: [NAME: {name}, URL:{url}]
            - SaaS Description: [{description}]
            
            TASK/OBJECTIVE:
            Identify the most critical as well as the none critical pain points based on user feedback for a given SaaS product and propose 1–2 highly targeted micro-SaaS solutions that directly address these issues. The proposed solutions may either:
            - Supplement the existing SaaS as a plugin, extension, or add-on that enhances its functionality, or
            - Compete as an independent tool, solving the identified issues in a superior way and potentially capturing market share.

            The AI should extract insights from user feedback across relevant platforms (e.g., ProductHunt, G2, Trustpilot, Reddit, Twitter, official forums) by examining the provided SaaS product (via its Name, URL, and Description, if available) to determine its pain points and recommend actionable micro-SaaS opportunities.

            Please ensure the final output is a valid JSON object with separate keys for each category, and that each array contains individual JSON objects (do not include inline comments in the output).
    
            OUTPUT FORMAT (JSON):
            
            {{
            "SaaS_Product": {{
                "Name": "NAME",
                "URL": "URL",
                "Description": "Give your description from your analysis if not provided by the user"
            }},
            "Prioritized_Pain_Points": [
                {{
                "Category": "Onboarding/UX/Performance/Integrations",
                "Pain_Point": "Specific issue (e.g., slow load times for image-heavy pages)",
                "Severity": "High/Medium (based on frequency and sentiment)",
                "Evidence": "Example user quote or metric from reviews"
                }}
                // Additional pain point objects if applicable.
            ],
            "Top_MicroSaaS_Ideas": [
                {{
                "Name": "Unique Tool Name",
                "Core_Problem_Solved": "Clear problem statement",
                "Solution_Description": "How it solves the pain point better than the original product",
                "Key_Features": "Must-have features (e.g., one-click optimization)",
                "Target_Audience": "Specific segment (e.g., solo creators, small agencies)",
                "Validation": {{
                    "Market_Gap": "No existing tools for [specific use case]",
                    "Feasibility": "Low-code/no-code friendly or existing APIs to leverage",
                    "Monetization_Potential": "Pricing model (e.g., $10/mo for power users)"
                }}
                }}
                // Optionally, a second idea can be provided.
            ]
            }}
        """ 
     
    
    return render(request, {"input": input})


def create_analysis_prompt(name, url, description=""):
    return f"""
    INPUT:
    - SaaS Product Name/URL: [NAME: {name}, URL: {url}]
    - SaaS Description: [{description}]

    TASK/OBJECTIVE:
    Conduct a comprehensive analysis of the specified SaaS product to identify market opportunities and pain points, following these steps:

    1. INITIAL RESEARCH PHASE:
    - Analyze the product's core features and value proposition
    - Identify primary user segments and use cases
    - Map the competitive landscape
    - Review pricing strategy and business model

    2. DATA COLLECTION SOURCES:
    Gather user feedback and sentiment from:
    - Product reviews (G2, Capterra, TrustPilot etc)
    - Community discussions (Reddit, Twitter, LinkedIn)
    - Technical forums (StackOverflow, GitHub Issues)
    - Product feedback boards
    - User interviews and testimonials
    - Feature request threads
    - Competitor comparison discussions

    3. ANALYSIS CRITERIA:
    Evaluate pain points based on:
    - Frequency of mention
    - Sentiment intensity
    - Impact on user workflow
    - Technical feasibility of solution
    - Market size of affected users
    - Revenue potential
    - Implementation complexity

    OUTPUT FORMAT (JSON):
    {{
        "SaaS_Product": {{
            "Name": "NAME",
            "URL": "URL",
            "Description": "Comprehensive description based on analysis",
            "Core_Features": [
                "Feature 1",
                "Feature 2"
            ],
            "Target_Market": [
                "Primary user segment",
                "Secondary user segment"
            ],
            "Current_Pricing": {{
                "Model": "Freemium/Premium/Enterprise",
                "Price_Range": "Price points",
                "Key_Limitations": [
                    "Limitation 1",
                    "Limitation 2"
                ]
            }}
        }},
        "Market_Analysis": {{
            "Total_Reviews_Analyzed": "Number",
            "Sentiment_Overview": {{
                "Positive": "Percentage",
                "Neutral": "Percentage",
                "Negative": "Percentage"
            }},
            "Key_Competitors": [
                {{
                    "Name": "Competitor name",
                    "Differential": "Key difference"
                }}
            ]
        }},
        "Prioritized_Pain_Points": [
            {{
                "Category": "UX/Performance/Integration/etc.",
                "Pain_Point": "Specific issue description",
                "Severity": "High/Medium/Low",
                "Frequency": "Percentage of mentions",
                "Impact": "Business impact description",
                "Affected_Segments": [
                    "User segment 1",
                    "User segment 2"
                ],
                "Evidence": [
                    {{
                        "Source": "Platform name",
                        "Quote": "User quote",
                        "Date": "Approximate date",
                        "Sentiment": "Negative/Neutral/Positive"
                    }}
                ]
            }}
        ],
        "Opportunity_Analysis": {{
            "Market_Gaps": [
                {{
                    "Gap": "Description",
                    "Size": "Estimated market size",
                    "Validation": "Evidence of demand"
                }}
            ],
            "Technical_Feasibility": {{
                "Available_APIs": [
                    "API 1 description",
                    "API 2 description"
                ],
                "Integration_Points": [
                    "Integration point 1",
                    "Integration point 2"
                ]
            }}
        }},
        "MicroSaaS_Recommendations": [
            {{
                "Name": "Product name",
                "Type": "Plugin/Standalone/Integration",
                "Core_Problem": "Primary pain point addressed",
                "Solution_Description": "Detailed solution approach",
                "Key_Features": [
                    {{
                        "Feature": "Feature name",
                        "Purpose": "Problem it solves",
                        "Priority": "Must-have/Nice-to-have"
                    }}
                ],
                "Target_Audience": {{
                    "Primary": "Main user segment",
                    "Secondary": "Additional segments",
                    "Market_Size": "Estimated TAM"
                }},
                "Business_Model": {{
                    "Revenue_Model": "Subscription/One-time/Usage-based",
                    "Pricing_Strategy": "Pricing tiers and rationale",
                    "Expected_MRR": "Revenue projection"
                }},
                "Implementation": {{
                    "Technical_Stack": [
                        "Technology 1",
                        "Technology 2"
                    ],
                    "Development_Timeline": "Estimated timeline",
                    "Resource_Requirements": "Team/Skills needed"
                }},
                "Go_To_Market": {{
                    "Distribution_Channels": [
                        "Channel 1",
                        "Channel 2"
                    ],
                    "Marketing_Strategy": "Key marketing approaches",
                    "Growth_Metrics": "KPIs to track"
                }}
            }}
        ]
    }}

    ADDITIONAL GUIDELINES:
    - All findings must be based on actual user feedback and market data
    - Pain points should be validated across multiple sources
    - Solutions should have clear differentiation from existing offerings
    - Include specific evidence and examples where possible
    - Focus on actionable opportunities with clear market demand
    - Consider both technical feasibility and business viability
    """
