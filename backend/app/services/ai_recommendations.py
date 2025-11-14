"""
AI Recommendation Service using LongCat API
Provides AI-powered recommendations for fixing compliance issues
"""
import os
import json
from typing import List, Dict, Any, Optional
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class AIRecommendationService:
    """Service for getting AI recommendations from LongCat API"""
    
    def __init__(self):
        self.api_key = os.getenv("LONGCAT_API_KEY", "")
        self.base_url = "https://api.longcat.chat/openai/v1/chat/completions"
        self.model = "LongCat-Flash-Chat"
    
    async def get_recommendations(
        self, 
        axe_results: Any, 
        failed_checks: List[Dict[str, Any]]
    ) -> Optional[str]:
        """
        Get AI recommendations for failed compliance checks
        
        Args:
            axe_results: The original axe-core scan results
            failed_checks: List of failed compliance checks
            
        Returns:
            AI-generated recommendations string
        """
        if not self.api_key:
            return None
        
        try:
            # Build prompt for LongCat
            prompt = self._build_prompt(axe_results, failed_checks)
            
            # Call LongCat API
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.base_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": (
                                    "You are an accessibility expert helping developers fix "
                                    "web accessibility issues. Provide clear, actionable, and "
                                    "easy-to-understand recommendations. Use simple language "
                                    "and provide code examples when helpful."
                                )
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "max_tokens": 2000,
                        "temperature": 0.7
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "choices" in data and len(data["choices"]) > 0:
                        return data["choices"][0]["message"]["content"]
                else:
                    print(f"LongCat API error: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            print(f"Error getting AI recommendations: {e}")
            return None
    
    def _build_prompt(
        self, 
        axe_results: Any, 
        failed_checks: List[Dict[str, Any]]
    ) -> str:
        """Build the prompt for LongCat API"""
        
        # Summarize failed checks
        failed_summary = []
        for check in failed_checks:
            failed_summary.append(
                f"- {check['check_name']}: {check['description']}\n"
                f"  Issues found: {len(check['issues'])}\n"
                f"  Issues: {', '.join(check['issues'][:3])}"  # First 3 issues
            )
        
        # Get sample violations
        sample_violations = []
        for violation in axe_results.violations[:5]:  # First 5 violations
            sample_violations.append({
                "id": violation.get("id", "unknown"),
                "description": violation.get("description", ""),
                "help": violation.get("help", ""),
                "impact": violation.get("impact", "unknown")
            })
        
        prompt = f"""I've scanned a webpage for accessibility compliance and found {len(failed_checks)} failed compliance checks.

Failed Compliance Checks:
{chr(10).join(failed_summary)}

Sample Accessibility Violations Found:
{json.dumps(sample_violations, indent=2)}

Please provide:
1. A clear summary of the main accessibility issues
2. Specific, actionable recommendations for fixing each failed check
3. Code examples or best practices where helpful
4. Prioritize the most critical issues first

Make the recommendations easy to understand for developers who may not be accessibility experts. 
Use simple language and provide practical solutions.

Format your response in a clear, structured way with headings and bullet points."""

        return prompt

