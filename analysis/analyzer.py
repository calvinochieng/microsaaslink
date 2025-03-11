from decouple import config
from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
import re
import json

def gen(name, url): 
    name = name or None
    url = url or None
    description = ''
    prompt = f"""
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
            // Standalone is HIHGHLY PREFFERED
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
    client = genai.Client(api_key=config("GEMINI_API_KEY"))
    model_id = "gemini-2.0-flash"
    google_search_tool = Tool( google_search = GoogleSearch()  )

    response = client.models.generate_content(
        model=model_id,
        contents= prompt,
        config=GenerateContentConfig(
            tools=[google_search_tool],
            response_modalities=["TEXT"],
        )
    )
    print(response)
    print(response.candidates[0].grounding_metadata.web_search_queries)
    def process_response(response):
        try:
            saas_data_json = extract_analysis_data(response)
            if saas_data_json is None:
                raise ValueError("Failed to extract analysis data")
                
            search_queries = extract_search_queries(response)
            token_info = extract_token_info(response)
            
            return {
                'saas_data_json': saas_data_json,
                'search_queries': search_queries,
                'token_info': token_info
            }
        except Exception as e:
            print(f"Error in process_response: {str(e)}")
            return None

    processed_data = process_response(response)
    return processed_data  # Return the processed data


def extract_analysis_data(response):
    try:
        # Get the text from the first part
        json_text = response.text
        # print("Original text:", json_text[:100] + "...") # Debug print
        
        if not isinstance(json_text, str):
            print(f"Unexpected type: {type(json_text)}")
            return None
            
        # Clean up the JSON text
        if "```json" in json_text:
            # Extract content between ```json and ```
            match = re.search(r'```json\s*(.*?)\s*```', json_text, re.DOTALL)
            if match:
                json_text = match.group(1)
        elif "```" in json_text:
            # Extract content between ``` and ```
            match = re.search(r'```\s*(.*?)\s*```', json_text, re.DOTALL)
            if match:
                json_text = match.group(1)
                
        # Clean up the text
        json_text = json_text.strip()
        
        # Remove single backticks if they exist
        if json_text.startswith('`') and json_text.endswith('`'):
            json_text = json_text[1:-1].strip()
            
        # print("Cleaned JSON text:", json_text[:100] + "...") # Debug print
        
        # Try to parse the JSON
        try:
            parsed_data = json.loads(json_text)
            return parsed_data
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {str(e)}")
            print("Failed JSON text:", json_text)
            return None
            
    except Exception as e:
        print(f"Error in extract_analysis_data: {str(e)}")
        return None

def extract_search_queries(response):
    return response.candidates[0].grounding_metadata.web_search_queries

def extract_search_rendered_content(response):
    return response.candidates[0].grounding_metadata.search_entry_point.rendered_content

def extract_token_info(response):
    return {
        'prompt_tokens': response.usage_metadata.prompt_token_count,
        'candidate_tokens': response.usage_metadata.candidates_token_count,
        'total_tokens': response.usage_metadata.total_token_count
    }


def process_response(response):
    try:
        saas_data_json = extract_analysis_data(response)
        if saas_data_json is None:
            raise ValueError("Failed to extract analysis data")
            
        search_queries = extract_search_queries(response)
        token_info = extract_token_info(response)
        
        return {
            'saas_data_json': saas_data_json,
            'search_queries': search_queries,
            'token_info': token_info
        }
    except Exception as e:
        print(f"Error in process_response: {str(e)}")
        return None

















