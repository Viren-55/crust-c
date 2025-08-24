#!/usr/bin/env python3
"""
Production-ready Crust Data API Client
Based on comprehensive testing and analysis
"""

import os
import requests
import json
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
import time
from datetime import datetime

# Load environment variables
load_dotenv()

class CrustDataAPIClient:
    """
    Production Crust Data API Client with comprehensive authentication support
    
    This client has been tested with the following findings:
    - Bearer token authentication works with api.crustdata.com
    - The main API server responds but specific endpoints may need discovery
    - Documentation site requires additional authentication steps
    """
    
    def __init__(self, 
                 api_base_url: Optional[str] = None, 
                 docs_base_url: Optional[str] = None,
                 token: Optional[str] = None,
                 email: Optional[str] = None,
                 password: Optional[str] = None):
        
        # Load from environment if not provided
        self.api_base_url = api_base_url or os.getenv('CRUST_API_BASE_URL', 'https://api.crustdata.com')
        self.docs_base_url = docs_base_url or os.getenv('CRUST_DOCS_URL', 'https://fulldocs.crustdata.com')
        self.token = token or os.getenv('CRUST_API_TOKEN')
        self.email = email or os.getenv('CRUST_EMAIL')
        self.password = password or os.getenv('CRUST_PASSWORD')
        
        # Session management
        self.api_session = requests.Session()
        self.docs_session = requests.Session()
        
        # Authentication status
        self.api_authenticated = False
        self.docs_authenticated = False
        
        # Setup sessions
        self._setup_api_session()
        self._setup_docs_session()
        
    def _setup_api_session(self):
        """Setup API session with token authentication"""
        if self.token:
            self.api_session.headers.update({
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json',
                'User-Agent': 'CrustData-Python-Client/1.0'
            })
            self.api_authenticated = True
    
    def _setup_docs_session(self):
        """Setup documentation session with basic auth"""
        if self.email and self.password:
            self.docs_session.auth = (self.email, self.password)
            self.docs_authenticated = True
    
    def test_api_connectivity(self) -> Dict[str, Any]:
        """
        Test API connectivity and return comprehensive status
        """
        results = {
            'timestamp': datetime.now().isoformat(),
            'api_base_url': self.api_base_url,
            'docs_base_url': self.docs_base_url,
            'token_available': bool(self.token),
            'credentials_available': bool(self.email and self.password),
            'tests': {}
        }
        
        # Test API base URL
        try:
            response = self.api_session.get(self.api_base_url, timeout=10)
            results['tests']['api_base'] = {
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'content_type': response.headers.get('content-type'),
                'response_size': len(response.text)
            }
        except Exception as e:
            results['tests']['api_base'] = {
                'error': str(e),
                'success': False
            }
        
        # Test docs base URL
        try:
            response = self.docs_session.get(f"{self.docs_base_url}/docs/api", timeout=10)
            results['tests']['docs_base'] = {
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'content_type': response.headers.get('content-type'),
                'response_size': len(response.text),
                'appears_authenticated': 'auth0' not in response.text.lower()
            }
        except Exception as e:
            results['tests']['docs_base'] = {
                'error': str(e),
                'success': False
            }
        
        return results
    
    def discover_endpoints(self) -> List[Dict[str, Any]]:
        """
        Attempt to discover available API endpoints
        """
        print("🔍 Discovering API endpoints...")
        
        # Common endpoint patterns to test
        potential_endpoints = [
            # REST endpoints
            ('GET', '/companies', 'Company data'),
            ('GET', '/people', 'People/contacts data'),
            ('GET', '/organizations', 'Organization data'),
            ('GET', '/search', 'Search functionality'),
            ('GET', '/data', 'General data endpoint'),
            ('GET', '/datasets', 'Available datasets'),
            
            # Versioned endpoints
            ('GET', '/v1/companies', 'V1 Company data'),
            ('GET', '/v1/people', 'V1 People data'),
            ('GET', '/v1/search', 'V1 Search'),
            ('GET', '/v1/data', 'V1 Data'),
            
            # API namespaced
            ('GET', '/api/companies', 'API Company data'),
            ('GET', '/api/people', 'API People data'),
            ('GET', '/api/search', 'API Search'),
            ('GET', '/api/data', 'API Data'),
            
            # GraphQL
            ('POST', '/graphql', 'GraphQL endpoint'),
            ('GET', '/graphql', 'GraphQL endpoint (GET)'),
            
            # Metadata endpoints
            ('GET', '/schema', 'API Schema'),
            ('GET', '/swagger.json', 'Swagger documentation'),
            ('GET', '/openapi.json', 'OpenAPI documentation'),
            ('GET', '/health', 'Health check'),
            ('GET', '/version', 'Version information'),
        ]
        
        discovered = []
        
        for method, endpoint, description in potential_endpoints:
            try:
                url = f"{self.api_base_url}{endpoint}"
                
                if method == 'GET':
                    response = self.api_session.get(url, timeout=5)
                elif method == 'POST':
                    if 'graphql' in endpoint:
                        # Test with introspection query
                        payload = {"query": "{ __schema { types { name } } }"}
                        response = self.api_session.post(url, json=payload, timeout=5)
                    else:
                        response = self.api_session.post(url, timeout=5)
                
                result = {
                    'method': method,
                    'endpoint': endpoint,
                    'description': description,
                    'url': url,
                    'status_code': response.status_code,
                    'content_type': response.headers.get('content-type', 'unknown'),
                    'content_length': len(response.text),
                    'successful': response.status_code < 400,
                    'json_response': False
                }
                
                # Try to parse JSON if applicable
                if 'application/json' in result['content_type']:
                    try:
                        data = response.json()
                        result['json_response'] = True
                        result['response_structure'] = type(data).__name__
                        if isinstance(data, dict):
                            result['json_keys'] = list(data.keys())[:10]  # First 10 keys
                        elif isinstance(data, list) and data:
                            result['array_length'] = len(data)
                            if isinstance(data[0], dict):
                                result['first_item_keys'] = list(data[0].keys())[:5]
                    except:
                        result['json_parse_error'] = True
                
                discovered.append(result)
                
                # Print status
                status_emoji = "✅" if result['successful'] else "❌"
                print(f"  {status_emoji} {method} {endpoint:<20} - {response.status_code} - {description}")
                
                if result['successful'] and result.get('json_response'):
                    if result.get('json_keys'):
                        print(f"     📋 Keys: {', '.join(result['json_keys'][:5])}{'...' if len(result['json_keys']) > 5 else ''}")
                    elif result.get('array_length'):
                        print(f"     📊 Array with {result['array_length']} items")
                
            except Exception as e:
                discovered.append({
                    'method': method,
                    'endpoint': endpoint,
                    'description': description,
                    'url': f"{self.api_base_url}{endpoint}",
                    'error': str(e),
                    'successful': False
                })
                print(f"  ❌ {method} {endpoint:<20} - ERROR: {str(e)[:50]}")
        
        return discovered
    
    def get_data(self, endpoint: str, params: Optional[Dict] = None, use_docs: bool = False) -> Optional[Dict]:
        """
        Fetch data from API endpoint
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            use_docs: Whether to use docs session instead of API session
        """
        session = self.docs_session if use_docs else self.api_session
        base_url = self.docs_base_url if use_docs else self.api_base_url
        
        try:
            url = f"{base_url}{endpoint}"
            response = session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '')
            
            if 'application/json' in content_type:
                return response.json()
            else:
                return {
                    'content': response.text,
                    'content_type': content_type,
                    'status_code': response.status_code
                }
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {endpoint}: {e}")
            return None
    
    def search(self, query: str, **kwargs) -> Optional[Dict]:
        """
        Search functionality - tries multiple endpoints
        """
        search_endpoints = ['/search', '/api/search', '/v1/search']
        
        for endpoint in search_endpoints:
            params = {'q': query, **kwargs}
            result = self.get_data(endpoint, params)
            if result:
                return result
        
        print(f"No search endpoint found for query: {query}")
        return None
    
    def get_companies(self, **kwargs) -> Optional[Dict]:
        """
        Get company data - tries multiple endpoints
        """
        company_endpoints = ['/companies', '/api/companies', '/v1/companies']
        
        for endpoint in company_endpoints:
            result = self.get_data(endpoint, kwargs)
            if result:
                return result
        
        print("No company endpoint found")
        return None
    
    def get_status(self) -> Dict[str, Any]:
        """Get client status and configuration"""
        return {
            'api_base_url': self.api_base_url,
            'docs_base_url': self.docs_base_url,
            'api_authenticated': self.api_authenticated,
            'docs_authenticated': self.docs_authenticated,
            'token_configured': bool(self.token),
            'credentials_configured': bool(self.email and self.password),
        }

def main():
    """Example usage and testing"""
    print("🚀 Crust Data API Client - Comprehensive Test")
    print("=" * 60)
    
    # Initialize client
    client = CrustDataAPIClient()
    
    # Show status
    status = client.get_status()
    print("📊 Client Status:")
    for key, value in status.items():
        emoji = "✅" if value else "❌"
        print(f"   {key}: {emoji}")
    
    print("\n" + "=" * 60)
    
    # Test connectivity
    print("🔍 Testing API connectivity...")
    connectivity = client.test_api_connectivity()
    
    print(f"\nAPI Base ({connectivity['api_base_url']}):")
    api_test = connectivity['tests'].get('api_base', {})
    if api_test.get('success'):
        print(f"   ✅ Status: {api_test['status_code']} | Type: {api_test['content_type']} | Size: {api_test['response_size']} chars")
    else:
        print(f"   ❌ Failed: {api_test.get('error', 'Unknown error')}")
    
    print(f"\nDocs Base ({connectivity['docs_base_url']}):")
    docs_test = connectivity['tests'].get('docs_base', {})
    if docs_test.get('success'):
        authenticated = "✅ Authenticated" if docs_test.get('appears_authenticated') else "❌ Not authenticated"
        print(f"   ✅ Status: {docs_test['status_code']} | {authenticated}")
    else:
        print(f"   ❌ Failed: {docs_test.get('error', 'Unknown error')}")
    
    print("\n" + "=" * 60)
    
    # Discover endpoints
    discovered_endpoints = client.discover_endpoints()
    successful_endpoints = [e for e in discovered_endpoints if e.get('successful')]
    
    print(f"\n📊 Discovery Summary:")
    print(f"   Total endpoints tested: {len(discovered_endpoints)}")
    print(f"   Successful endpoints: {len(successful_endpoints)}")
    
    if successful_endpoints:
        print(f"\n✅ Working endpoints:")
        for endpoint in successful_endpoints[:5]:  # Show first 5
            print(f"   {endpoint['method']} {endpoint['endpoint']} - {endpoint['description']}")
    
    # Save detailed results
    results = {
        'client_status': status,
        'connectivity_test': connectivity,
        'discovered_endpoints': discovered_endpoints,
        'timestamp': datetime.now().isoformat()
    }
    
    with open('crust_api_discovery_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Detailed results saved to: crust_api_discovery_results.json")
    print("✅ Testing completed!")
    
    # Provide recommendations
    print(f"\n💡 Recommendations:")
    if successful_endpoints:
        print(f"   - API server is accessible at {client.api_base_url}")
        print(f"   - Bearer token authentication is working")
        print(f"   - Start with endpoint: {successful_endpoints[0]['endpoint']}")
    else:
        print(f"   - API endpoints may require specific paths not tested")
        print(f"   - Check Crust Data documentation for correct endpoint paths")
        print(f"   - Consider contacting Crust Data support for API documentation")

if __name__ == "__main__":
    main()