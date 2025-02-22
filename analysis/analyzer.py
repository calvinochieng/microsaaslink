from decouple import config
import google.generativeai as genai

def gen(name, url):
    genai.configure(api_key=config("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-2.0-flash')
    name = name or None
    url = url or None
    description = ""
    
    input = f"""
    INPUT:
    - SaaS Product Name/URL: [NAME: {name}, URL: {url}]
    - SaaS Description: [{description}]

    TASK/OBJECTIVE: 
    Conduct a comprehensive analysis of the specified SaaS product to two or more micro-SaaS opportunities based on the users pain points, following these steps:

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
        "saas_product": {{
            "name": "NAME",
            "url": "URL",
            "description": "Comprehensive description based on analysis",
            "core_features": [
                "Feature 1",
                "Feature 2"
            ],
            "target_market": [
                "Primary user segment",
                "Secondary user segment"
            ],
            "current_pricing": {{
                "model": "Freemium/Premium/Enterprise",
                "price_range": "Price points",
                "key_limitations": [
                    "Limitation 1",
                    "Limitation 2"
                ]
            }}
        }},
        "market_analysis": {{
            "total_reviews_analyzed": "Number",
            //sentiment_overview MUST BE PERCENTAGE NUMBER, IF CANT BE FOUND JUST PUT 0% ON ALL
            "sentiment_overview": {{
                "positive": "Percentage",
                "neutral": "Percentage",
                "negative": "Percentage"
            }},
            "key_competitors": [
                {{
                    "name": "Competitor name",
                    "differential": "Key difference"
                }}
            ]
        }},
        "prioritized_pain_points": [
            {{
                "category": "UX/Performance/Integration/etc.",
                "pain_point": "Specific issue description",
                "severity": "High/Medium/Low",
                "frequency": "Percentage of mentions",
                "impact": "Business impact description",
                "affected_segments": [
                    "User segment 1",
                    "User segment 2"
                ],
                "evidence": [
                    {{
                        "source": "Platform name",
                        "quote": "User quote",
                        "date": "Approximate date",
                        "sentiment": "Negative/Neutral/Positive"
                    }}
                ]
            }}
        ],
        "opportunity_analysis": {{
            "market_gaps": [
                {{
                    "gap": "Description",
                    "size": "Estimated market size",
                    "validation": "Evidence of demand"
                }}
            ],
            "technical_feasibility": {{
                "available_apis": [
                    "API 1 description",
                    "API 2 description"
                ],
                "integration_points": [
                    "Integration point 1",
                    "Integration point 2"
                ]
            }}
        }},
        "microsaas_recommendations": [
            {{
                "name": "Product name",
                "type": "Plugin/Standalone/Integration",
                "core_problem": "Primary pain point addressed",
                "solution_description": "Detailed solution approach",
                "key_features": [
                    {{
                        "feature": "Feature name",
                        "purpose": "Problem it solves",
                        "priority": "Must-have/Nice-to-have"
                    }}
                ],
                "target_audience": {{
                    "primary": "Main user segment",
                    "secondary": "Additional segments",
                    "market_size": "Estimated TAM"
                }},
                "business_model": {{
                    "revenue_model": "Subscription/One-time/Usage-based",
                    "pricing_strategy": "Pricing tiers and rationale",
                    "expected_mrr": "Revenue projection"
                }},
                "implementation": {{
                    "technical_stack": [
                        "Technology 1",
                        "Technology 2"
                    ],
                    "development_timeline": "Estimated timeline",
                    "resource_requirements": "Team/Skills needed"
                }},
                "go_to_market": {{
                    "distribution_channels": [
                        "Channel 1",
                        "Channel 2"
                    ],
                    "marketing_strategy": "Key marketing approaches",
                    "growth_metrics": "KPIs to track"
                }}
            }}
        ]
    }}

    ADDITIONAL GUIDELINES:
    - All findings must be based on actual user feedback and market data
    - Pain points should be validated across multiple sources
    - Solutions should have clear differentiation from existing offerings
    - Include specific evidence and examples where possible, with source links
    - Focus on actionable opportunities with clear market demand
    - Consider both technical feasibility and business viability
    """
    
    response = model.generate_content(input)
    return response.text


#     from decouple import config
# import google.generativeai as genai
# import json

# def gen(name, url):
#     genai.configure(api_key=config("GEMINI_API_KEY"))
#     model = genai.GenerativeModel('gemini-2.0-flash')
#     name = name or None
#     url = url or None
#     description = ""

#     input = f"""Is there water in these planets , mar, jupitar, return the item is json
#     """

#     response = model.generate_content(input)

#     try:
#         # Extract the generated text (assuming you want the first candidate)
#         generated_text = response.candidates[0].text

#         # Parse the JSON string
#         json_data = json.loads(generated_text)  # This is the crucial step

#         return json_data  # Now you have a Python dictionary

#     except (json.JSONDecodeError, IndexError) as e:
#         print(f"Error: Could not parse JSON or access candidate: {e}")
#         return {"error": "Could not process the request."}  # Return an error object

# # Example usage (for testing)
# result = gen(None, None)
# print(result)
