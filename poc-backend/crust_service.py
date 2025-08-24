"""
Crust Data integration service for company discovery
"""

import os
from typing import List, Dict, Any
from crust_working_api_client import CrustDataClient
from models import ICP
import asyncio
from concurrent.futures import ThreadPoolExecutor

class CrustService:
    """Service for discovering companies using Crust Data API"""
    
    def __init__(self):
        self.client = CrustDataClient()
        self.executor = ThreadPoolExecutor(max_workers=4)
        
    async def find_companies(self, icp: ICP) -> List[Dict[str, Any]]:
        """Find companies matching ICP criteria using Crust Discovery API"""
        
        # Build filters for the discovery API
        filters = self._build_discovery_filters(icp)
        
        # Fetch company data using discovery API (run in thread pool to avoid blocking)
        loop = asyncio.get_event_loop()
        companies = await loop.run_in_executor(
            self.executor,
            self._fetch_companies_by_filters,
            filters
        )
        
        print(f"🎯 Found {len(companies)} companies from discovery API")
        return companies
    
    def _build_discovery_filters(self, icp: ICP) -> Dict[str, Any]:
        """Build filters for Crust Discovery API based on ICP criteria"""
        
        conditions = []
        
        # Industry filter - use multiple fields like the real estate example
        if icp.industries:
            industry_conditions = []
            for industry in icp.industries:
                # Search in multiple industry-related fields for better coverage
                industry_conditions.extend([
                    {"column": "linkedin_industries", "type": "(.)", "value": industry, "allow_null": True},
                    {"column": "linkedin_categories", "type": "(.)", "value": industry, "allow_null": True},
                    {"column": "crunchbase_categories", "type": "(.)", "value": industry, "allow_null": True},
                    {"column": "markets", "type": "(.)", "value": industry, "allow_null": True}
                ])
            
            # Use OR for industry matching (any of the selected industries in any field)
            conditions.append({
                "op": "or", 
                "conditions": industry_conditions
            })
        
        # Headcount filter - using correct Crust API operators
        if icp.headcount_min is not None and icp.headcount_max is not None:
            conditions.extend([
                {"column": "linkedin_headcount", "type": "=>", "value": icp.headcount_min, "allow_null": False},
                {"column": "linkedin_headcount", "type": "=<", "value": icp.headcount_max, "allow_null": False}
            ])
        
        # Revenue filter - using correct Crust API operators
        if icp.revenue_min is not None and icp.revenue_max is not None:
            conditions.extend([
                {"column": "estimated_revenue_lower_bound_usd", "type": "=>", "value": icp.revenue_min, "allow_null": False},
                {"column": "estimated_revenue_lower_bound_usd", "type": "=<", "value": icp.revenue_max, "allow_null": False}
            ])
        
        filters = {
            "op": "and",
            "conditions": conditions
        }
        
        print(f"🔍 Built discovery filters: {filters}")
        return filters
    
    def _fetch_companies_by_filters(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch companies using Crust Discovery API with filters"""
        try:
            print(f"🔍 Calling Crust Discovery API with filters...")
            
            # Build complete payload with required fields
            payload = {
                "filters": filters,
                "hidden_columns": [],
                "offset": 0,
                "count": 50,
                "sorts": []
            }
            
            # Use the _make_request method directly with proper payload
            response = self.client._make_request('POST', '/screener/screen/', json=payload)
            
            print(f"📊 Discovery API response type: {type(response)}")
            print(f"📊 Discovery API response keys: {list(response.keys()) if isinstance(response, dict) else 'Not a dict'}")
            
            if isinstance(response, dict):
                # Check if it's an error response
                if 'error' in response:
                    print(f"❌ API Error: {response.get('error')}")
                    return []
                
                # Extract companies from response
                if 'rows' in response and 'fields' in response:
                    companies_data = response['rows']
                    fields = [field['api_name'] for field in response.get('fields', [])]
                    
                    print(f"📊 Found {len(companies_data)} companies")
                    print(f"📊 Available fields: {fields[:10]}...")  # Show first 10 fields
                    
                    # Convert rows to dict format
                    companies = []
                    for row_data in companies_data:
                        company = {}
                        for i, field_name in enumerate(fields):
                            if i < len(row_data):
                                company[field_name] = row_data[i]
                        companies.append(company)
                    
                    print(f"📊 Sample company: {companies[0].get('company_name') if companies else 'None'}")
                    return companies
                else:
                    print(f"📊 Unexpected response structure: {list(response.keys())}")
                    return []
            else:
                print(f"📊 Unexpected response type: {type(response)}")
                return []
                
        except Exception as e:
            print(f"❌ Error calling discovery API: {e}")
            return []
    
    def _fetch_company_data(self, domains: List[str]) -> List[Dict[str, Any]]:
        """Fetch company data from Crust API (blocking operation)"""
        try:
            # Limit to first 50 domains for POC performance
            limited_domains = domains[:50]
            print(f"🔍 Fetching data for {len(limited_domains)} domains: {limited_domains[:5]}...")
            
            fields = [
                'company_name', 'company_website_domain',
                'headcount.linkedin_headcount',
                'estimated_revenue_lower_bound_usd', 
                'headquarters', 'year_founded',
                'taxonomy.linkedin_industries',
                'taxonomy.crunchbase_categories'
            ]
            
            companies = self.client.get_company_data(limited_domains, fields=fields)
            print(f"📊 Raw API response type: {type(companies)}")
            print(f"📊 Raw API response length: {len(companies) if isinstance(companies, list) else 'Not a list'}")
            
            if isinstance(companies, list) and len(companies) > 0:
                print(f"📊 First company sample keys: {list(companies[0].keys())}")
                print(f"📊 First company name: {companies[0].get('company_name')}")
                return companies
            elif companies:
                print(f"📊 Single company response keys: {list(companies.keys())}")
                return [companies]
            else:
                print("📊 Empty response from API")
                return []
                
        except Exception as e:
            print(f"❌ Error fetching company data: {e}")
            return []
    
    def _get_domains_by_industry(self, industries: List[str]) -> List[str]:
        """Get relevant company domains based on target industries"""
        
        # Industry-specific domain mappings (this would be more sophisticated in production)
        industry_domains = {
            'Technology': [
                'google.com', 'microsoft.com', 'apple.com', 'meta.com',
                'netflix.com', 'tesla.com', 'nvidia.com', 'intel.com',
                'cisco.com', 'ibm.com', 'oracle.com'
            ],
            'Software': [
                'salesforce.com', 'adobe.com', 'sap.com', 'servicenow.com',
                'workday.com', 'splunk.com', 'vmware.com', 'autodesk.com',
                'intuit.com', 'dropbox.com'
            ],
            'Fintech': [
                'stripe.com', 'square.com', 'paypal.com', 'coinbase.com',
                'robinhood.com', 'plaid.com', 'affirm.com', 'klarna.com',
                'chime.com', 'sofi.com'
            ],
            'E-commerce': [
                'amazon.com', 'shopify.com', 'etsy.com', 'ebay.com',
                'wayfair.com', 'chewy.com', 'overstock.com', 'wish.com',
                'poshmark.com', 'mercari.com'
            ],
            'SaaS': [
                'hubspot.com', 'slack.com', 'zoom.us', 'notion.so',
                'asana.com', 'trello.com', 'monday.com', 'airtable.com',
                'figma.com', 'canva.com', 'atlassian.com'
            ],
            'Healthcare': [
                'teladoc.com', 'veracyte.com', 'moderna.com', 'illumina.com',
                'dexcom.com', 'intuitive.com', 'medtronic.com'
            ],
            'Manufacturing': [
                'ge.com', 'caterpillar.com', 'boeing.com', 'lockheed.com',
                'honeywell.com', '3m.com', 'emerson.com'
            ],
            'Retail': [
                'walmart.com', 'target.com', 'costco.com', 'homedepot.com',
                'lowes.com', 'bestbuy.com', 'macys.com'
            ]
        }
        
        # Collect domains from all selected industries
        domains = []
        for industry in industries:
            industry_key = industry.strip()
            if industry_key in industry_domains:
                domains.extend(industry_domains[industry_key])
            else:
                # Fallback to general tech companies for unknown industries
                domains.extend(industry_domains['Technology'][:5])
        
        # Remove duplicates while preserving order
        unique_domains = list(dict.fromkeys(domains))
        
        # Add some general high-quality companies
        additional_domains = [
            'airbnb.com', 'uber.com', 'lyft.com', 'pinterest.com',
            'twitter.com', 'snapchat.com', 'linkedin.com', 'reddit.com',
            'twitch.tv', 'discord.com', 'github.com', 'gitlab.com'
        ]
        unique_domains.extend([d for d in additional_domains if d not in unique_domains])
        
        return unique_domains
    
    def _matches_icp_criteria(self, company: Dict[str, Any], icp: ICP) -> bool:
        """Check if company matches ICP criteria"""
        
        # Extract employee count
        headcount_data = company.get('headcount', {})
        if isinstance(headcount_data, dict):
            emp_count = headcount_data.get('linkedin_headcount', 0)
        else:
            emp_count = 0
            
        # Extract revenue
        revenue = company.get('estimated_revenue_lower_bound_usd', 0)
        
        # Check headcount range
        if emp_count > 0:  # Only filter if we have headcount data
            if not (icp.headcount_min <= emp_count <= icp.headcount_max):
                return False
                
        # Check revenue range
        if revenue > 0:  # Only filter if we have revenue data
            if not (icp.revenue_min <= revenue <= icp.revenue_max):
                return False
        
        # Check industry match (at least one industry should match)
        company_industries = []
        taxonomy = company.get('taxonomy', {})
        if isinstance(taxonomy, dict):
            linkedin_industries = taxonomy.get('linkedin_industries', [])
            crunchbase_categories = taxonomy.get('crunchbase_categories', [])
            company_industries = linkedin_industries + crunchbase_categories
        
        # If we have industry data, ensure at least one matches
        if company_industries:
            industry_match = any(
                any(target.lower() in comp_industry.lower() or comp_industry.lower() in target.lower() 
                    for comp_industry in company_industries)
                for target in icp.industries
            )
            if not industry_match:
                return False
                
        return True
    
    def get_company_by_domain(self, domain: str) -> Dict[str, Any]:
        """Get detailed information for a specific company"""
        try:
            result = self.client.get_company_data(domain)
            if isinstance(result, list) and result:
                return result[0]
            elif result:
                return result
            return {}
        except Exception as e:
            print(f"Error fetching company data for {domain}: {e}")
            return {}