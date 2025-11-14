from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os

from app.services.compliance_checker import ComplianceChecker, AxeCoreResult
from app.services.ai_recommendations import AIRecommendationService

app = FastAPI(title="ComplyScan API", version="1.0.0")

# CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
compliance_checker = ComplianceChecker()
ai_service = AIRecommendationService()




class ComplianceCheckResult(BaseModel):
    """Model for individual compliance check result"""
    check_id: str
    check_name: str
    passed: bool
    issues: List[str]
    recommendation: Optional[str] = None


class ComplianceResponse(BaseModel):
    """Model for API response"""
    score: float
    total_checks: int
    passed_checks: int
    failed_checks: int
    checks: List[ComplianceCheckResult]
    ai_recommendations: Optional[str] = None


@app.get("/")
async def root():
    return {
        "message": "ComplyScan API",
        "version": "1.0.0",
        "endpoints": {
            "POST /analyze": "Analyze axe-core results and return compliance score with AI recommendations"
        }
    }


@app.post("/analyze", response_model=ComplianceResponse)
async def analyze_compliance(axe_results: AxeCoreResult):
    """
    Analyze axe-core scan results against 10 compliance checks
    and provide AI-powered recommendations
    """
    try:
        # Run compliance checks
        compliance_results = compliance_checker.check_all(axe_results)
        
        # Calculate score
        total_checks = len(compliance_results)
        passed_checks = sum(1 for check in compliance_results if check["passed"])
        failed_checks = total_checks - passed_checks
        score = (passed_checks / total_checks * 100) if total_checks > 0 else 0
        
        # Get AI recommendations for failed checks
        failed_checks_list = [
            check for check in compliance_results if not check["passed"]
        ]
        
        ai_recommendations = None
        if failed_checks_list:
            try:
                ai_recommendations = await ai_service.get_recommendations(
                    axe_results, failed_checks_list
                )
            except Exception as e:
                print(f"AI recommendation error: {e}")
                # Continue without AI recommendations if service fails
        
        # Format response
        response = ComplianceResponse(
            score=round(score, 2),
            total_checks=total_checks,
            passed_checks=passed_checks,
            failed_checks=failed_checks,
            checks=[
                ComplianceCheckResult(
                    check_id=check["check_id"],
                    check_name=check["check_name"],
                    passed=check["passed"],
                    issues=check["issues"],
                    recommendation=check.get("recommendation")
                )
                for check in compliance_results
            ],
            ai_recommendations=ai_recommendations
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing compliance: {str(e)}")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

