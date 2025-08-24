"""
FastAPI backend for POC Outreach Workflow
ICP Definition -> Company Discovery -> Scoring -> Results
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List
import time
import asyncio
from dotenv import load_dotenv
from pydantic import BaseModel

from models import ICP, CompanyResult, SearchResponse, PeopleResponse
from crust_service import CrustService
from scoring_service import ScoringService
from people_service import PeopleService

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="POC Outreach Workflow API",
    description="API for discovering and scoring companies based on ICP criteria using Crust Data",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
crust_service = CrustService()
scoring_service = ScoringService()
people_service = PeopleService()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "POC Outreach Workflow API",
        "status": "running",
        "version": "1.0.0",
        "endpoints": [
            "/search-companies",
            "/company/{domain}/people",
            "/send-email",
            "/company/{domain}",
            "/health"
        ]
    }

# Email request model
class EmailRequest(BaseModel):
    recipient_email: str
    recipient_name: str
    recipient_title: str
    company_name: str
    linkedin_profile_url: str = None

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "services": {
            "crust_api": "connected",
            "scoring": "ready"
        }
    }

@app.post("/search-companies", response_model=SearchResponse)
async def search_companies(icp: ICP):
    """
    Search for companies matching ICP criteria
    
    - **industries**: List of target industries
    - **revenue_min/max**: Revenue range in USD
    - **headcount_min/max**: Employee count range
    
    Returns scored and ranked companies from Crust Data
    """
    
    start_time = time.time()
    
    try:
        print(f"🔍 Searching companies for ICP: {icp.industries}")
        print(f"   Revenue: ${icp.revenue_min:,} - ${icp.revenue_max:,}")
        print(f"   Headcount: {icp.headcount_min} - {icp.headcount_max}")
        
        # Step 1: Find companies using Crust Data
        print("   📊 Fetching company data from Crust API...")
        companies = await crust_service.find_companies(icp)
        print(f"   ✅ Found {len(companies)} companies matching criteria")
        
        # Step 2: Score and rank companies
        print("   🎯 Scoring and ranking companies...")
        scored_companies = scoring_service.score_companies(companies, icp)
        print(f"   ✅ Scored companies, top score: {scored_companies[0].score:.3f}" if scored_companies else "   ⚠️ No companies to score")
        
        # Step 3: Return top results
        top_companies = scored_companies[:20]  # Return top 20
        
        search_time_ms = int((time.time() - start_time) * 1000)
        
        response = SearchResponse(
            companies=top_companies,
            total_found=len(scored_companies),
            search_time_ms=search_time_ms,
            icp=icp
        )
        
        print(f"   🚀 Returning {len(top_companies)} companies (search took {search_time_ms}ms)")
        
        return response
        
    except Exception as e:
        print(f"❌ Error in search_companies: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error searching companies: {str(e)}"
        )

@app.get("/company/{domain}/people", response_model=PeopleResponse)
async def get_company_decision_makers(domain: str, company_name: str = None):
    """
    Get decision makers for a specific company
    
    - **domain**: Company domain (e.g., hubspot.com)
    - **company_name**: Optional company name for better search results
    
    Returns top 5 decision makers from the company
    """
    
    try:
        print(f"👥 Getting decision makers for company: {domain}")
        
        # If company name not provided, try to extract from domain
        if not company_name:
            company_name = domain.replace('.com', '').replace('.', ' ').title()
        
        # Find decision makers using people service
        decision_makers = await people_service.find_decision_makers(company_name, domain)
        
        if not decision_makers:
            print(f"⚠️ No decision makers found for {domain}")
        
        response = PeopleResponse(
            decision_makers=decision_makers,
            company_name=company_name,
            company_domain=domain,
            total_found=len(decision_makers)
        )
        
        print(f"   👥 Returning {len(decision_makers)} decision makers")
        return response
        
    except Exception as e:
        print(f"❌ Error getting decision makers: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting decision makers: {str(e)}"
        )

@app.post("/send-email")
async def send_personalized_email(email_request: EmailRequest):
    """
    Send personalized email to a decision maker
    
    - **recipient_email**: Email address of the recipient
    - **recipient_name**: Full name of the recipient
    - **recipient_title**: Job title of the recipient
    - **company_name**: Company name
    - **linkedin_profile_url**: Optional LinkedIn profile URL
    
    Returns email sending status
    """
    
    try:
        print(f"📧 Sending personalized email to {email_request.recipient_name} at {email_request.company_name}")
        
        # Import and use the personalized email sender
        import subprocess
        import json
        
        # Prepare the profile data for the email sender
        profile_data = {
            "product_vision": "Our cutting-edge POC Outreach Workflow helps businesses discover ideal customers, score prospects, and send personalized outreach emails at scale using AI-powered insights from Crust Data.",
            "linkedin_profile": json.dumps([{
                "business_email": [email_request.recipient_email],
                "current_employers": [{
                    "employer_name": email_request.company_name,
                    "business_emails": {
                        email_request.recipient_email: {
                            "verification_status": "verified",
                            "last_validated_at": "2025-01-24"
                        }
                    }
                }],
                "name": email_request.recipient_name,
                "title": email_request.recipient_title,
                "linkedin_profile_url": email_request.linkedin_profile_url or ""
            }])
        }
        
        # Call the personalized email sender
        process = subprocess.run(
            ["python", "../personlized_email_sender.py"],
            input=json.dumps(profile_data),
            text=True,
            capture_output=True,
            cwd="/Users/birendra/Downloads/crust_data/crust-c"
        )
        
        if process.returncode == 0:
            print(f"   ✅ Email sent successfully to {email_request.recipient_email}")
            return {
                "status": "success",
                "message": f"Personalized email sent to {email_request.recipient_name}",
                "recipient": email_request.recipient_email
            }
        else:
            error_msg = process.stderr.strip() or "Unknown error"
            print(f"   ❌ Email sending failed: {error_msg}")
            return {
                "status": "error", 
                "message": f"Failed to send email: {error_msg}",
                "recipient": email_request.recipient_email
            }
        
    except Exception as e:
        print(f"❌ Error sending email: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error sending email: {str(e)}"
        )

@app.get("/company/{domain}")
async def get_company_details(domain: str):
    """Get detailed information for a specific company"""
    
    try:
        print(f"🔍 Getting details for company: {domain}")
        
        company_data = crust_service.get_company_by_domain(domain)
        
        if not company_data:
            raise HTTPException(
                status_code=404,
                detail=f"Company not found: {domain}"
            )
        
        return company_data
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting company details: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting company details: {str(e)}"
        )

@app.get("/industries")
async def get_available_industries():
    """Get list of available industries for ICP selection"""
    return {
        "industries": [
            "Technology",
            "Software", 
            "Fintech",
            "E-commerce",
            "SaaS",
            "Healthcare",
            "Manufacturing",
            "Retail",
            "Consulting",
            "Marketing",
            "Education",
            "Real Estate",
            "Transportation",
            "Energy",
            "Media"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting POC Outreach Workflow API...")
    print("   📊 Crust Data integration: Ready")
    print("   🎯 Company scoring: Ready")
    print("   🌐 Server: http://localhost:8000")
    print("   📖 Docs: http://localhost:8000/docs")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        reload=True,
        log_level="info"
    )