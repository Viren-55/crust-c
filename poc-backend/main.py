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

from models import ICP, CompanyResult, SearchResponse
from crust_service import CrustService
from scoring_service import ScoringService

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

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "POC Outreach Workflow API",
        "status": "running",
        "version": "1.0.0",
        "endpoints": [
            "/search-companies",
            "/company/{domain}",
            "/health"
        ]
    }

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