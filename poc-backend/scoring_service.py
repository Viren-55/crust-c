"""
Company scoring service for ranking companies by ICP fit
"""

from typing import List, Dict, Any
from models import ICP, CompanyResult

class ScoringService:
    """Service for scoring and ranking companies based on ICP fit"""
    
    def score_companies(self, companies: List[Dict[str, Any]], icp: ICP) -> List[CompanyResult]:
        """Score companies and return sorted results"""
        
        scored_companies = []
        
        for company in companies:
            score = self._calculate_icp_score(company, icp)
            
            # Convert to CompanyResult format
            result = self._convert_to_result(company, score)
            scored_companies.append(result)
        
        # Sort by score (highest first) and return
        return sorted(scored_companies, key=lambda x: x.score, reverse=True)
    
    def _calculate_icp_score(self, company: Dict[str, Any], icp: ICP) -> float:
        """Calculate ICP fit score for a company (0.0 to 1.0)"""
        
        total_score = 0.0
        max_possible_score = 1.0
        
        # Industry Match Score (40% of total)
        industry_score = self._score_industry_match(company, icp) * 0.4
        total_score += industry_score
        
        # Company Size Score (30% of total)
        size_score = self._score_size_match(company, icp) * 0.3
        total_score += size_score
        
        # Revenue Score (20% of total)
        revenue_score = self._score_revenue_match(company, icp) * 0.2
        total_score += revenue_score
        
        # Growth/Quality Indicators (10% of total)
        quality_score = self._score_quality_indicators(company) * 0.1
        total_score += quality_score
        
        return min(total_score, max_possible_score)
    
    def _score_industry_match(self, company: Dict[str, Any], icp: ICP) -> float:
        """Score industry alignment (0.0 to 1.0)"""
        
        # Extract company industries
        company_industries = []
        taxonomy = company.get('taxonomy', {})
        if isinstance(taxonomy, dict):
            linkedin_industries = taxonomy.get('linkedin_industries', [])
            crunchbase_categories = taxonomy.get('crunchbase_categories', [])
            company_industries = linkedin_industries + crunchbase_categories
        
        if not company_industries:
            return 0.5  # Neutral score if no industry data
        
        # Check for exact matches first
        exact_matches = 0
        partial_matches = 0
        
        for target_industry in icp.industries:
            target_lower = target_industry.lower()
            
            for company_industry in company_industries:
                company_lower = company_industry.lower()
                
                # Exact match
                if target_lower == company_lower:
                    exact_matches += 1
                    break
                # Partial match (contains)
                elif target_lower in company_lower or company_lower in target_lower:
                    partial_matches += 1
                    break
        
        # Calculate score based on matches
        total_targets = len(icp.industries)
        
        if exact_matches > 0:
            return min(1.0, 0.8 + (exact_matches / total_targets) * 0.2)
        elif partial_matches > 0:
            return min(0.8, 0.4 + (partial_matches / total_targets) * 0.4)
        else:
            return 0.2  # Low score but not zero
    
    def _score_size_match(self, company: Dict[str, Any], icp: ICP) -> float:
        """Score company size alignment (0.0 to 1.0)"""
        
        headcount_data = company.get('headcount', {})
        if isinstance(headcount_data, dict):
            emp_count = headcount_data.get('linkedin_headcount', 0)
        else:
            emp_count = 0
        
        if emp_count == 0:
            return 0.5  # Neutral score if no headcount data
        
        # Perfect match if within range
        if icp.headcount_min <= emp_count <= icp.headcount_max:
            return 1.0
        
        # Partial score if close to range
        range_size = icp.headcount_max - icp.headcount_min
        tolerance = range_size * 0.5  # 50% tolerance
        
        if emp_count < icp.headcount_min:
            distance = icp.headcount_min - emp_count
            if distance <= tolerance:
                return max(0.3, 1.0 - (distance / tolerance) * 0.7)
        
        if emp_count > icp.headcount_max:
            distance = emp_count - icp.headcount_max
            if distance <= tolerance:
                return max(0.3, 1.0 - (distance / tolerance) * 0.7)
        
        return 0.1  # Very low score if far from range
    
    def _score_revenue_match(self, company: Dict[str, Any], icp: ICP) -> float:
        """Score revenue alignment (0.0 to 1.0)"""
        
        revenue = company.get('estimated_revenue_lower_bound_usd', 0)
        
        if revenue == 0:
            return 0.5  # Neutral score if no revenue data
        
        # Perfect match if within range
        if icp.revenue_min <= revenue <= icp.revenue_max:
            return 1.0
        
        # Partial score if close to range
        range_size = icp.revenue_max - icp.revenue_min
        tolerance = range_size * 0.5  # 50% tolerance
        
        if revenue < icp.revenue_min:
            distance = icp.revenue_min - revenue
            if distance <= tolerance:
                return max(0.3, 1.0 - (distance / tolerance) * 0.7)
        
        if revenue > icp.revenue_max:
            distance = revenue - icp.revenue_max
            if distance <= tolerance:
                return max(0.3, 1.0 - (distance / tolerance) * 0.7)
        
        return 0.1  # Very low score if far from range
    
    def _score_quality_indicators(self, company: Dict[str, Any]) -> float:
        """Score company quality indicators (0.0 to 1.0)"""
        
        quality_score = 0.0
        
        # Recent founding (growth potential)
        founded_year = company.get('year_founded')
        if founded_year and founded_year.isdigit():
            year = int(founded_year)
            current_year = 2025
            age = current_year - year
            
            if 5 <= age <= 20:  # Sweet spot for growth companies
                quality_score += 0.3
            elif age < 5:  # Very new, some risk
                quality_score += 0.2
            elif age > 20:  # Established, stable
                quality_score += 0.25
        
        # Has headquarters information (data completeness)
        headquarters = company.get('headquarters') or company.get('hq_street_address') or company.get('hq_country')
        if headquarters:
            quality_score += 0.2
        
        # Has detailed industry classification
        taxonomy = company.get('taxonomy', {})
        if isinstance(taxonomy, dict):
            linkedin_industries = taxonomy.get('linkedin_industries', [])
            if len(linkedin_industries) >= 2:
                quality_score += 0.2
        
        # Large headcount (established company)
        headcount_data = company.get('headcount', {})
        if isinstance(headcount_data, dict):
            emp_count = headcount_data.get('linkedin_headcount', 0)
            if emp_count >= 100:
                quality_score += 0.15
            elif emp_count >= 500:
                quality_score += 0.25
        
        # High revenue (successful company)
        revenue = company.get('estimated_revenue_lower_bound_usd', 0)
        if revenue >= 10000000:  # $10M+
            quality_score += 0.15
        
        return min(quality_score, 1.0)
    
    def _convert_to_result(self, company: Dict[str, Any], score: float) -> CompanyResult:
        """Convert company data to CompanyResult format"""
        
        # Extract headcount
        headcount_data = company.get('headcount', {})
        if isinstance(headcount_data, dict):
            headcount = headcount_data.get('linkedin_headcount', 0)
        else:
            headcount = 0
        
        # Extract industries
        industries = []
        taxonomy = company.get('taxonomy', {})
        if isinstance(taxonomy, dict):
            linkedin_industries = taxonomy.get('linkedin_industries', [])
            crunchbase_categories = taxonomy.get('crunchbase_categories', [])
            industries = linkedin_industries + crunchbase_categories
        
        # Remove duplicates and limit to top 3
        unique_industries = list(dict.fromkeys(industries))[:3]
        
        # Extract headquarters (try multiple fields)
        headquarters = company.get('headquarters') or company.get('hq_street_address') or company.get('hq_country')
        
        return CompanyResult(
            name=company.get('company_name', 'Unknown Company'),
            domain=company.get('company_website_domain', ''),
            headcount=headcount,
            revenue=company.get('estimated_revenue_lower_bound_usd', 0),
            headquarters=headquarters,
            score=round(score, 3),
            industries=unique_industries,
            founded_year=company.get('year_founded')
        )