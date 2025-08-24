#!/usr/bin/env python3
"""
Working Crust Data API Client - Based on actual API documentation
This client uses the correct endpoints discovered from crust_company_api.md
"""

import os
import requests
import json
from typing import Dict, List, Optional, Any, Union
from dotenv import load_dotenv
import time
from datetime import datetime

# Load environment variables
load_dotenv()

class CrustDataClient:
    """
    Working Crust Data API Client with correct endpoints and authentication
    
    Based on analysis of crust_company_api.md, the correct patterns are:
    - Base URL: https://api.crustdata.com
    - Auth: Authorization: Token <your_token>
    - Main endpoints: /screener/company, /screener/screen/, etc.
    """
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv('CRUST_API_TOKEN')
        self.base_url = 'https://api.crustdata.com'
        
        if not self.token:
            raise ValueError("API token is required. Set CRUST_API_TOKEN environment variable or pass token parameter.")
        
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Token {self.token}',  # Note: "Token" not "Bearer"
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': 'CrustData-Python-Client/2.0'
        })
    
    def get_company_data(self, 
                        company_domain: Union[str, List[str]], 
                        fields: Optional[List[str]] = None) -> Dict:
        """
        Get company data by domain(s)
        
        Args:
            company_domain: Single domain string or list of domains
            fields: Specific fields to retrieve (e.g., ['company_name', 'headcount.linkedin_headcount'])
        
        Returns:
            Company data response
        """
        endpoint = '/screener/company'
        
        # Handle multiple domains
        if isinstance(company_domain, list):
            domain_param = ','.join(company_domain)
        else:
            domain_param = company_domain
        
        params = {'company_domain': domain_param}
        
        # Add fields if specified
        if fields:
            params['fields'] = ','.join(fields)
        
        return self._make_request('GET', endpoint, params=params)
    
    def get_company_people(self, 
                          company_domain: str, 
                          limit: Optional[int] = None,
                          fields: Optional[List[str]] = None) -> Dict:
        """
        Get people data for a company
        
        Args:
            company_domain: Company domain
            limit: Maximum number of results
            fields: Specific fields to retrieve
        """
        endpoint = '/screener/company/people'
        
        params = {'company_domain': company_domain}
        
        if limit:
            params['limit'] = limit
        if fields:
            params['fields'] = ','.join(fields)
        
        return self._make_request('GET', endpoint, params=params)
    
    def search_companies(self, 
                        query: Dict[str, Any],
                        limit: Optional[int] = None,
                        offset: Optional[int] = None) -> Dict:
        """
        Search companies using POST endpoint
        
        Args:
            query: Search query parameters
            limit: Maximum number of results
            offset: Results offset for pagination
        """
        endpoint = '/screener/company/search'
        
        payload = query.copy()
        if limit:
            payload['limit'] = limit
        if offset:
            payload['offset'] = offset
        
        return self._make_request('POST', endpoint, json=payload)
    
    def screen_companies(self, 
                        filters: Dict[str, Any],
                        limit: Optional[int] = None) -> Dict:
        """
        Screen companies with advanced filters
        
        Args:
            filters: Screening filters
            limit: Maximum number of results
        """
        endpoint = '/screener/screen/'
        
        payload = filters.copy()
        if limit:
            payload['limit'] = limit
        
        return self._make_request('POST', endpoint, json=payload)
    
    def identify_company(self, 
                        company_info: Dict[str, Any]) -> Dict:
        """
        Identify a company using various identifiers
        
        Args:
            company_info: Company identification info (name, domain, etc.)
        """
        endpoint = '/screener/identify'
        
        return self._make_request('POST', endpoint, json=company_info)
    
    def get_linkedin_posts(self, 
                          company_domain: Optional[str] = None,
                          keyword_search: Optional[str] = None,
                          limit: Optional[int] = None) -> Dict:
        """
        Get LinkedIn posts for companies
        
        Args:
            company_domain: Company domain
            keyword_search: Keyword to search for
            limit: Maximum number of results
        """
        if keyword_search:
            endpoint = '/screener/linkedin_posts/keyword_search/'
            params = {'keyword_search': keyword_search}
        else:
            endpoint = '/screener/linkedin_posts/'
            params = {}
        
        if company_domain:
            params['company_domain'] = company_domain
        if limit:
            params['limit'] = limit
        
        return self._make_request('POST' if keyword_search else 'GET', endpoint, 
                                params=params if not keyword_search else None,
                                json=params if keyword_search else None)
    
    def _make_request(self, 
                     method: str, 
                     endpoint: str, 
                     params: Optional[Dict] = None,
                     json: Optional[Dict] = None) -> Dict:
        """
        Make HTTP request to API
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            params: Query parameters
            json: JSON payload
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=params, timeout=30)
            elif method.upper() == 'POST':
                response = self.session.post(url, params=params, json=json, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            
            # Try to parse JSON response
            try:
                return response.json()
            except json.JSONDecodeError:
                return {
                    'content': response.text,
                    'content_type': response.headers.get('content-type'),
                    'status_code': response.status_code
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'error': str(e),
                'status_code': getattr(e.response, 'status_code', None),
                'endpoint': endpoint,
                'method': method
            }
    
    def test_connection(self) -> Dict[str, Any]:
        """Test API connection with a simple company lookup"""
        print("🧪 Testing Crust Data API connection...")
        
        test_results = {
            'timestamp': datetime.now().isoformat(),
            'token_provided': bool(self.token),
            'base_url': self.base_url,
            'tests': {}
        }
        
        # Test 1: Simple company lookup
        print("   Testing company data endpoint...")
        try:
            result = self.get_company_data('google.com', fields=['company_name', 'headcount.linkedin_headcount'])
            test_results['tests']['company_data'] = {
                'success': 'error' not in result,
                'response_keys': list(result.keys()) if isinstance(result, dict) else None,
                'has_data': bool(result and 'error' not in result)
            }
            if test_results['tests']['company_data']['success']:
                print("   ✅ Company data endpoint working")
            else:
                print(f"   ❌ Company data failed: {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results['tests']['company_data'] = {'success': False, 'error': str(e)}
            print(f"   ❌ Company data exception: {e}")
        
        # Test 2: Multiple domains
        print("   Testing multiple domains...")
        try:
            result = self.get_company_data(['google.com', 'apple.com'], fields=['company_name'])
            test_results['tests']['multiple_domains'] = {
                'success': 'error' not in result,
                'response_keys': list(result.keys()) if isinstance(result, dict) else None,
            }
            if test_results['tests']['multiple_domains']['success']:
                print("   ✅ Multiple domains working")
            else:
                print(f"   ❌ Multiple domains failed: {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results['tests']['multiple_domains'] = {'success': False, 'error': str(e)}
            print(f"   ❌ Multiple domains exception: {e}")
        
        # Test 3: Company people endpoint
        print("   Testing company people endpoint...")
        try:
            result = self.get_company_people('google.com', limit=5)
            test_results['tests']['company_people'] = {
                'success': 'error' not in result,
                'response_keys': list(result.keys()) if isinstance(result, dict) else None,
            }
            if test_results['tests']['company_people']['success']:
                print("   ✅ Company people endpoint working")
            else:
                print(f"   ❌ Company people failed: {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results['tests']['company_people'] = {'success': False, 'error': str(e)}
            print(f"   ❌ Company people exception: {e}")
        
        return test_results

# Convenience functions for common use cases
def get_company_profile(domain: str, detailed: bool = False) -> Dict:
    """
    Quick function to get company profile
    
    Args:
        domain: Company domain
        detailed: Whether to get detailed information
    """
    client = CrustDataClient()
    
    if detailed:
        fields = [
            'company_name', 'company_website_domain', 'headquarters',
            'year_founded', 'estimated_revenue_lower_bound_usd', 'estimated_revenue_higher_bound_usd',
            'headcount.linkedin_headcount', 'linkedin_company_description',
            'taxonomy.linkedin_industries', 'taxonomy.crunchbase_categories',
            'competitors.competitor_website_domains'
        ]
    else:
        fields = ['company_name', 'headquarters', 'headcount.linkedin_headcount', 'linkedin_company_description']
    
    return client.get_company_data(domain, fields=fields)

def search_tech_companies(industry: Optional[str] = None, min_employees: Optional[int] = None) -> Dict:
    """
    Search for technology companies
    
    Args:
        industry: Industry filter
        min_employees: Minimum employee count
    """
    client = CrustDataClient()
    
    query = {
        'taxonomy': {
            'linkedin_industries': ['Technology', 'Software', 'Internet']
        }
    }
    
    if industry:
        query['taxonomy']['linkedin_industries'].append(industry)
    
    if min_employees:
        query['headcount'] = {
            'linkedin_headcount': {'$gte': min_employees}
        }
    
    return client.search_companies(query, limit=50)

def main():
    """Test the working API client"""
    print("🚀 Crust Data Working API Client Test")
    print("=" * 60)
    
    try:
        client = CrustDataClient()
        
        # Test connection
        test_results = client.test_connection()
        
        print(f"\n📊 Test Summary:")
        successful_tests = sum(1 for test in test_results['tests'].values() if test.get('success', False))
        total_tests = len(test_results['tests'])
        print(f"   Successful tests: {successful_tests}/{total_tests}")
        
        if successful_tests > 0:
            print(f"\n✅ API is working! Example usage:")
            
            # Example 1: Get company profile
            print(f"\n1. Company Profile Example:")
            profile = get_company_profile('hubspot.com')
            if 'error' not in profile:
                print(f"   ✅ Successfully retrieved company profile")
                if isinstance(profile, dict) and 'data' in profile:
                    print(f"   Sample keys: {list(profile.keys())}")
            else:
                print(f"   ❌ Error: {profile.get('error')}")
            
            # Example 2: Multiple companies
            print(f"\n2. Multiple Companies Example:")
            multiple = client.get_company_data(['google.com', 'microsoft.com'], 
                                             fields=['company_name', 'headcount.linkedin_headcount'])
            if 'error' not in multiple:
                print(f"   ✅ Successfully retrieved multiple companies")
                if isinstance(multiple, dict):
                    print(f"   Response keys: {list(multiple.keys())}")
                elif isinstance(multiple, list):
                    print(f"   Response: Array with {len(multiple)} items")
                else:
                    print(f"   Response type: {type(multiple)}")
            else:
                print(f"   ❌ Error: {multiple.get('error') if hasattr(multiple, 'get') else multiple}")
        
        else:
            print(f"\n❌ API connection failed. Check:")
            print(f"   - Token is correct: {client.token[:20]}...")
            print(f"   - Network connectivity")
            print(f"   - API endpoint availability")
        
        # Save results
        with open('crust_working_api_test.json', 'w') as f:
            json.dump(test_results, f, indent=2, default=str)
        print(f"\n💾 Test results saved to: crust_working_api_test.json")
        
    except Exception as e:
        print(f"❌ Setup error: {e}")

if __name__ == "__main__":
    main()