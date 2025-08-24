"""
Data models for the POC Outreach Workflow
"""

from pydantic import BaseModel, Field
from typing import List, Optional

class ICP(BaseModel):
    """Ideal Customer Profile definition"""
    industries: List[str] = Field(..., description="Target industries")
    revenue_min: int = Field(..., description="Minimum annual revenue in USD", ge=0)
    revenue_max: int = Field(..., description="Maximum annual revenue in USD", ge=0)
    headcount_min: int = Field(..., description="Minimum employee count", ge=0)
    headcount_max: int = Field(..., description="Maximum employee count", ge=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "industries": ["Technology", "Software"],
                "revenue_min": 1000000,
                "revenue_max": 100000000,
                "headcount_min": 50,
                "headcount_max": 1000
            }
        }

class CompanyResult(BaseModel):
    """Company search result with scoring"""
    name: str
    domain: str
    headcount: int
    revenue: int
    headquarters: Optional[str] = None
    score: float = Field(..., description="ICP fit score (0-1)")
    industries: List[str] = []
    founded_year: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "HubSpot",
                "domain": "hubspot.com",
                "headcount": 11096,
                "revenue": 1000000000,
                "headquarters": "2 Canal Park",
                "score": 0.85,
                "industries": ["Software", "Marketing Technology"],
                "founded_year": "2006"
            }
        }

class SearchResponse(BaseModel):
    """Response from company search"""
    companies: List[CompanyResult]
    total_found: int
    search_time_ms: int
    icp: ICP