from decouple import config
from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
import re
import json
import time
from datetime import datetime
import os
# Marker
from django.shortcuts import get_object_or_404

class MultiStepSaaSAnalyzer:
    def __init__(self, project_id=None, api_key=None):
        """Initialize the SaaS Analyzer with a Gemini API key and project ID"""
        from multianalysis.models import Project  # Import here to avoid circular imports
        
        self.api_key = api_key or config("GEMINI_API_KEY")
        self.client = genai.Client(api_key=self.api_key)
        self.model_id = "gemini-2.0-flash"  # Using a powerful model for analysis
        self.google_search_tool = Tool(google_search=GoogleSearch())
        
        # If project_id is provided, load the project
        self.project = None
        if project_id:
            self.project = get_object_or_404(Project, id=project_id)
            
            # Load existing data if available
            self.target_saas = self.project.target_saas or {
                'name': None,
                'url': None,
                'description': None,
                'target_audience': None,
                'differential_factor': None,
                'pain_points': []
            }
            self.competitors = self.project.competitors or []
            self.competitor_pain_points = self.project.competitor_pain_points or {}
            self.combined_pain_points = self.project.combined_pain_points or []
            self.micro_saas_ideas = self.project.micro_saas_ideas or []
        else:
            # Default empty structures
            self.target_saas = {
                'name': None,
                'url': None,
                'description': None,
                'target_audience': None,
                'differential_factor': None,
                'pain_points': []
            }
            self.competitors = []
            self.competitor_pain_points = {}
            self.combined_pain_points = []
            self.micro_saas_ideas = []
        
    def analyze_target_saas(self, name, url=None):
        """Step 1: Analyze the target SaaS company"""
        print(f"\n{'='*80}\nSTEP 1: ANALYZING TARGET SAAS: {name}\n{'='*80}")
        
        prompt = f"""
        You are a SaaS market analyst conducting a thorough analysis of a target SaaS product.
        
        INPUT:
        - SaaS Product Name: {name}
        - SaaS Product URL: {url or "Not provided"}
        
        TASK:
        Conduct a comprehensive analysis of this SaaS product and provide the following details in a structured JSON format:
        
        1. Basic information (name, url, description)
        2. Target audience (be specific about industries, company sizes, roles)
        3. Key features and benefits 
        4. Differential factors (what makes this SaaS stand out)
        5. Common user pain points (identify at least 5 specific pain points based on user feedback, reviews, and common complaints)
        
        Format your response as a clean JSON object with these keys: Any text you add must not be formated in markdown
        {{
            'name': 'name', 
            'url': 'https://domainname', 
            'description': 'description', 
            'target_audience': ["adience 1", "audience 2",.... ],
            'key_features': ["feature 1", "feature 2",.... ], 
            'differential_factor': 'differnatial factor here', 
            'pain_points': [{{'issue': 'described issue ', 'severity': integer}}, .......]
        }}
        
        For pain_points, provide an array of objects with "issue" and "severity" (1-10) keys.
        """
        
        try:
            response = self._generate_content(prompt)
            result = self._extract_json(response.text)
            print(result)
            
            if result:
                self.target_saas = result
                self._print_target_analysis(result)
                
                # Update the project model
                if self.project:
                    self.project.name = result['name']
                    self.project.url = result['url']
                    self.project.description = result['description']
                    self.project.target_saas = result
                    self.project.save()
                
                return result
            else:
                print("Failed to analyze target SaaS. Please try again.")
                return None
        except Exception as e:
            print(f"Error in analyze_target_saas: {str(e)}")
            return None
    
    def identify_competitors(self, competitor_count=4):
        """Step 2: Identify main competitors of the target SaaS"""
        if not self.target_saas['name']:
            print("Error: Please analyze a target SaaS first.")
            return None
            
        print(f"\n{'='*80}\nSTEP 2: IDENTIFYING COMPETITORS for {self.target_saas['name']}\n{'='*80}")
        
        prompt = f"""
        You are a SaaS market analyst identifying the main competitors for a target SaaS product.
        
        TARGET SAAS INFORMATION:
        - Name: {self.target_saas['name']}
        - URL: {self.target_saas['url']}
        - Description: {self.target_saas['description']}
        - Target Audience: {self.target_saas['target_audience']}
        - Differential Factor: {self.target_saas['differential_factor']}
        
        TASK:
        Identify the top {competitor_count} direct competitors for this SaaS product. For each competitor, provide:
        
        1. Name
        2. URL
        3. Brief description
        4. Target audience
        5. Key differential factor compared to the target SaaS
        
        Format your response as a clean JSON array where each object has keys DO NOT FOMART ANY TEXT INTO MARKDOWN:
          [
            {{
            "name":"Competitor name",
            "url": "https://domainname",
            "description":"competitor description",
            "target_audience":["adience 1","audience 2",... ], 
            "differential_factor":"string factor"
            }},....
          ]
        """
        
        try:
            response = self._generate_content(prompt)
            result = self._extract_json(response.text)
            print(result)
            
            if result:
                self.competitors = result
                self._print_competitor_analysis(result)
                
                # Update the project model
                if self.project:
                    self.project.competitors = result
                    self.project.save()
                
                return result
            else:
                print("Failed to identify competitors. Please try again.")
                return None
        except Exception as e:
            print(f"Error in identify_competitors: {str(e)}")
            return None
    
    def analyze_competitor_pain_points(self):
        """Step 3: Analyze pain points for each competitor"""
        if not self.competitors:
            print("Error: No competitors identified. Please identify competitors first.")
            return None
            
        print(f"\n{'='*80}\nSTEP 3: ANALYZING COMPETITOR PAIN POINTS\n{'='*80}")
        
        self.competitor_pain_points = {}
        
        for competitor in self.competitors:
            comp_name = competitor['name']
            print(f"\n{'-'*40}\nAnalyzing pain points for: {comp_name}\n{'-'*40}")
            
            prompt = f"""
            You are a SaaS market analyst researching user pain points for a specific SaaS product.
            
            COMPETITOR INFORMATION:
            - Name: {comp_name}
            - URL: {competitor['url']}
            - Description: {competitor['description']}
            - Target Audience: {competitor['target_audience']}
            
            TASK:
            Based on online reviews, user feedback forums, and common complaints, identify at least 5 specific pain points that users experience with this SaaS product.
            
            For each pain point:
            1. Describe the specific issue/complaint
            2. Rate its severity on a scale of 1-10
            3. Indicate how common this complaint is
            4. Note whether the company appears to be addressing this issue
            
            Format your response as a clean JSON array where each object has keys:
            "issue", "severity", "frequency", "being_addressed"
            """
            
            try:
                response = self._generate_content(prompt)
                result = self._extract_json(response.text)
                print(result)
                
                if result:
                    self.competitor_pain_points[comp_name] = result
                    self._print_pain_points(comp_name, result)
                else:
                    print(f"Failed to analyze pain points for {comp_name}.")
            except Exception as e:
                print(f"Error analyzing pain points for {comp_name}: {str(e)}")
            
            # Add a brief delay between API calls
            time.sleep(1)
        
        print(self.competitor_pain_points)
        
        # Update the project model
        if self.project:
            self.project.competitor_pain_points = self.competitor_pain_points
            self.project.save()
        
        return self.competitor_pain_points
    
    def combine_pain_points(self):
        """Step 4: Combine all pain points to identify patterns and gaps"""
        if not self.target_saas['pain_points'] or not self.competitor_pain_points:
            print("Error: Pain points analysis not complete. Please analyze pain points first.")
            return None
            
        print(f"\n{'='*80}\nSTEP 4: COMBINING PAIN POINTS\n{'='*80}")
        
        # Prepare a summary of all pain points for the prompt
        all_points_summary = f"TARGET SAAS ({self.target_saas['name']}) PAIN POINTS:\n"
        for point in self.target_saas['pain_points']:
            all_points_summary += f"- {point['issue']} (Severity: {point['severity']})\n"
        
        all_points_summary += "\nCOMPETITOR PAIN POINTS:\n"
        for comp_name, points in self.competitor_pain_points.items():
            all_points_summary += f"\n{comp_name}:\n"
            for point in points:
                all_points_summary += f"- {point['issue']} (Severity: {point['severity']}, Being Addressed: {point['being_addressed']})\n"
        
        prompt = f"""
        You are a SaaS market analyst identifying patterns and market gaps from user pain points.
        
        PAIN POINTS DATA:
        {all_points_summary}
        
        TASK:
        1. Analyze all pain points from the target SaaS and its competitors
        2. Group similar pain points and identify patterns
        3. Determine which significant pain points are NOT being adequately addressed by any of the companies
        4. Identify market gaps (pain points with high severity that aren't being addressed well)
        
        Format your response as a clean JSON object with these keys:
        1. "patterns" - Array of objects with keys: "category", "description", "examples", "prevalence"
        2. "market_gaps" - Array of objects with keys: "gap", "severity", "opportunity_size", "explanation"
        
        Focus especially on uncovering meaningful market gaps that could lead to micro-SaaS opportunities.
        """
        
        try:
            response = self._generate_content(prompt)
            result = self._extract_json(response.text)
            print(result)
            
            if result:
                self.combined_pain_points = result
                self._print_combined_analysis(result)
                
                # Update the project model
                if self.project:
                    self.project.combined_pain_points = result
                    self.project.save()
                
                return result
            else:
                print("Failed to combine pain points. Please try again.")
                return None
        except Exception as e:
            print(f"Error in combine_pain_points: {str(e)}")
            return None
    
    def generate_micro_saas_ideas(self, max_ideas=3):
        """Step 5: Generate micro-SaaS ideas based on identified market gaps"""
        if not self.combined_pain_points:
            print("Error: Combined pain points analysis not complete. Please combine pain points first.")
            return None

        print(f"\n{'='*80}\nSTEP 5: GENERATING MICRO-SAAS IDEAS\n{'='*80}")

        # Extract market gaps for the prompt
        market_gaps = self.combined_pain_points.get('market_gaps', [])
        if not market_gaps:
            print("No significant market gaps identified to generate micro-SaaS ideas.")
            return None

        gaps_summary = ""
        for i, gap in enumerate(market_gaps, 1):
            gaps_summary += f"{i}. {gap['gap']} (Severity: {gap['severity']}, Opportunity: {gap['opportunity_size']})\n"
            gaps_summary += f"   Explanation: {gap['explanation']}\n\n"

        prompt = f"""
        You are a SaaS product strategist developing micro-SaaS ideas based on identified market gaps.
        
        

        IDENTIFIED MARKET GAPS:
        {gaps_summary}
        
        TASK:
        Generate {max_ideas} well-validated micro-SaaS product concepts based on these market gaps.
        
        IMPORTANT:
        - If the target SaaS does not meet these conditions, always recommend a standalone micro-SaaS solution that addresses the identified pain points.
        - HIGHLY RECOMMENDED It is acceptable to propose an idea that directly competes by solving a specific market segment more effectively than the target SaaS and its competitors, as described in the combined pain points.
        - INCASE YOU HAVE TO RECOMEND AN ADDON, PLUGIN, OR BROWSER EXTENTION idea(s), ensure that the target SaaS is open with APIs, supports add-ons, or allows the implementation of a browser extension, AND SHOW HOW IT WILL BE IMPLIMENTED USING THE PIS PROVIDED BY THE TARGET SAAS
        - Validate each idea based on its viability, feasibility, adaptability, and alignment with current market trends.
        
        For each micro-SaaS idea:
        1. Create a compelling name and tagline.
        2. Provide a concise description of the solution.
        3. Define the specific target audience.
        4. List 3-5 key features that directly address the market gap.
        5. Suggest a pricing model.
        6. Explain why this idea would succeed (include validation points).
        7. Estimate implementation difficulty (1-10).
        
        Format your response as a clean JSON array where each object has keys:
        "name", "tagline", "description", "target_audience", "key_features", "pricing_model", "validation", "implementation_difficulty".
        ORGANIZED THIS WAY
          {{
        "name": "MicroSaaS Name",
        "tagline": "Compelling tagline for the solution",
        "description": "A concise description of the solution and its value proposition.",
        "target_audience": "Define the specific target audience.",
        "key_features": ["Key Feature 1", "Key Feature 2", "Key Feature 3"],
        "pricing_model": "Pricing model details, tiers and prices",
        "validation": "Validation points: viability, feasibility, adaptability, and market trends",
        "implementation_difficulty": "Estimated difficulty on a scale of 1-10"
          }}

        
        Focus on creating highly focused, specialized solutions with a clear value proposition that could be built by a small team.
        """

        try:
            response = self._generate_content(prompt)
            result = self._extract_json(response.text)
            print(result)
            print("GAP SUMMERRY HERE =========", gaps_summary)

            if result:
                self.micro_saas_ideas = result
                self._print_micro_saas_ideas(result)
                
                # Update the project model
                if self.project:
                    self.project.micro_saas_ideas = result
                    self.project.status = True  # Mark as completed
                    self.project.save()
                
                return result
            else:
                print("Failed to generate micro-SaaS ideas. Please try again.")
                return None
        except Exception as e:
            print(f"Error in generate_micro_saas_ideas: {str(e)}")
            return None

    def save_analysis(self):
        """Save the complete analysis to the Project model instance instead of a JSON file."""
        if not self.target_saas.get('name'):
            print("No analysis to save. Please complete at least the first step.")
            return None

        analysis = {
            'target_saas': self.target_saas,
            'competitors': self.competitors,
            'competitor_pain_points': self.competitor_pain_points,
            'combined_pain_points': self.combined_pain_points,
            'micro_saas_ideas': self.micro_saas_ideas,
            'timestamp': datetime.now().isoformat(),
            'analysis_complete': bool(self.micro_saas_ideas)
        }

        try:
            # Update the project instance with the analysis data
            self.project.target_saas = self.target_saas
            self.project.competitors = self.competitors
            self.project.competitor_pain_points = self.competitor_pain_points
            self.project.combined_pain_points = self.combined_pain_points
            self.project.micro_saas_ideas = self.micro_saas_ideas
            
            # Optionally update a status flag to indicate analysis completion
            self.project.status = bool(self.micro_saas_ideas)
            self.project.save()

            print("\nComplete analysis saved to the Project model.")
            analysis['slug'] = self.project.slug
            analysis['name'] = self.project.name
            return analysis
        except Exception as e:
            print(f"Error saving analysis to model: {str(e)}")
            return None


    def full_analysis(self, name, url=None, max_ideas=3):
        """Run the complete multi-step analysis process"""
        print(f"\n{'='*80}\nBEGINNING FULL ANALYSIS FOR: {name}\n{'='*80}")
        
        # Step 1: Analyze target SaaS
        target = self.analyze_target_saas(name, url)
        if not target:
            return "Failed at Step 1: Target SaaS Analysis"
        
        # Step 2: Identify competitors
        competitors = self.identify_competitors()
        if not competitors:
            return "Failed at Step 2: Competitor Identification"
        
        # Step 3: Analyze competitor pain points
        comp_pain_points = self.analyze_competitor_pain_points()
        if not comp_pain_points:
            return "Failed at Step 3: Competitor Pain Point Analysis"
        
        # Step 4: Combine pain points
        combined = self.combine_pain_points()
        if not combined:
            return "Failed at Step 4: Pain Point Combination"
        
        # Step 5: Generate micro-SaaS ideas
        ideas = self.generate_micro_saas_ideas(max_ideas)
        if not ideas:
            return "Failed at Step 5: Micro-SaaS Idea Generation"
        
        # Save the complete analysis
        filename = self.save_analysis()
        
        print(f"\n{'='*80}\nANALYSIS COMPLETE\n{'='*80}")
        print(f"Generated {len(self.micro_saas_ideas)} micro-SaaS ideas based on market gaps")
        
        return {
            "status": "success",
            "target_saas": self.target_saas['name'],
            "competitors_analyzed": len(self.competitors),
            "market_gaps_identified": len(self.combined_pain_points.get('market_gaps', [])),
            "micro_saas_ideas": len(self.micro_saas_ideas),
            "result_file": filename
        }
    
    def _generate_content(self, prompt):
        """Helper method to generate content using Gemini API"""
        return self.client.models.generate_content(
            model=self.model_id,
            contents=prompt,
            config=GenerateContentConfig(
                tools=[self.google_search_tool],
                response_modalities=["TEXT"],
            )
        )
    
    def _extract_json(self, text):
        """Extract and parse JSON from Gemini response"""
        try:
            # Clean up the JSON text
            if "```json" in text:
                # Extract content between ```json and ```
                match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
                if match:
                    text = match.group(1)
            elif "```" in text:
                # Extract content between ``` and ```
                match = re.search(r'```\s*(.*?)\s*```', text, re.DOTALL)
                if match:
                    text = match.group(1)
            
            # Clean up the text
            text = text.strip()
            
            # Try to parse the JSON
            return json.loads(text)
        except Exception as e:
            print(f"JSON extraction error: {str(e)}")
            print(f"Failed to parse text: {text[:100]}...")
            return None
    
    def _print_target_analysis(self, result):
        """Print the target SaaS analysis in a readable format"""
        print(f"\n{'-'*40}\nTarget SaaS Analysis: {result['name']}\n{'-'*40}")
        print(f"URL: {result['url']}")
        print(f"Description: {result['description']}")
        print(f"Target Audience: {result['target_audience']}")
        print(f"Differential Factor: {result['differential_factor']}")
        
        print("\nKey Features:")
        for i, feature in enumerate(result.get('key_features', []), 1):
            print(f"{i}. {feature}")
        
        print("\nPain Points:")
        for i, point in enumerate(result.get('pain_points', []), 1):
            print(f"{i}. {point['issue']} (Severity: {point['severity']}/10)")
    
    def _print_competitor_analysis(self, competitors):
        """Print the competitor analysis in a readable format"""
        print(f"\n{'-'*40}\nCompetitor Analysis\n{'-'*40}")
        for i, comp in enumerate(competitors, 1):
            print(f"\n{i}. {comp['name']}")
            print(f"   URL: {comp['url']}")
            print(f"   Description: {comp['description']}")
            print(f"   Target Audience: {comp['target_audience']}")
            print(f"   Differential Factor: {comp['differential_factor']}")
    
    def _print_pain_points(self, competitor_name, pain_points):
        """Print competitor pain points in a readable format"""
        print(f"\nPain Points for {competitor_name}:")
        for i, point in enumerate(pain_points, 1):
            being_addressed = "✓" if point.get('being_addressed', False) else "✗"
            print(f"{i}. {point['issue']} (Severity: {point['severity']}/10, Being Addressed: {being_addressed})")
    
    def _print_combined_analysis(self, result):
        """Print the combined pain points analysis in a readable format"""
        print(f"\n{'-'*40}\nCombined Pain Points Analysis\n{'-'*40}")
        
        print("\nIdentified Patterns:")
        for i, pattern in enumerate(result.get('patterns', []), 1):
            print(f"{i}. {pattern['category']}: {pattern['description']}")
            print(f"   Prevalence: {pattern['prevalence']}")
            print(f"   Examples: {', '.join(pattern['examples'])}")
        
        print("\nMarket Gaps:")
        for i, gap in enumerate(result.get('market_gaps', []), 1):
            print(f"{i}. {gap['gap']}")
            print(f"   Severity: {gap['severity']}/10")
            print(f"   Opportunity Size: {gap['opportunity_size']}")
            print(f"   Explanation: {gap['explanation']}")
    
    def _print_micro_saas_ideas(self, ideas):
        """Print micro-SaaS ideas in a readable format"""
        print(f"\n{'-'*40}\nRecommended Micro-SaaS Opportunities\n{'-'*40}")
        
        for i, idea in enumerate(ideas, 1):
            print(f"\n{i}. {idea['name']}")
            print(f"   Tagline: {idea['tagline']}")
            print(f"   Description: {idea['description']}")
            print(f"   Target Audience: {idea['target_audience']}")
            
            print(f"   Key Features:")
            for j, feature in enumerate(idea['key_features'], 1):
                print(f"     {j}. {feature}")
            
            print(f"   Pricing Model: {idea['pricing_model']}")
            print(f"   Validation: {idea['validation']}")
            print(f"   Implementation Difficulty: {idea['implementation_difficulty']}/10")



# Example usage
if __name__ == "__main__":
    analyzer = MultiStepSaaSAnalyzer()
    
    # Option 1: Run the full analysis
    result = analyzer.full_analysis("Notion", "https://notion.so")
    
    # Option 2: Run the analysis step by step
    """
    analyzer.analyze_target_saas("Airtable", "https://airtable.com")
    analyzer.identify_competitors()
    analyzer.analyze_competitor_pain_points()
    analyzer.combine_pain_points()
    analyzer.generate_micro_saas_ideas(max_ideas=3)
    analyzer.save_analysis()
    """