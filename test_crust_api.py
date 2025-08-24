#!/usr/bin/env python3
"""
Test script to verify Crust Data API access with token authentication
"""

import os
import requests
import json
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class CrustAPITester:
    """Test Crust Data API connectivity and data fetching"""
    
    def __init__(self):
        self.email = os.getenv('CRUST_EMAIL')
        self.password = os.getenv('CRUST_PASSWORD')
        self.token = os.getenv('CRUST_API_TOKEN')
        self.docs_url = os.getenv('CRUST_DOCS_URL', 'https://fulldocs.crustdata.com')
        self.api_base_url = os.getenv('CRUST_API_BASE_URL', 'https://api.crustdata.com')
        
        self.session = requests.Session()
        
        # Set up headers with token
        if self.token:
            self.session.headers.update({
                'Authorization': f'Bearer {self.token}',
                'X-API-Key': self.token,
                'Content-Type': 'application/json'
            })
    
    def test_authentication_methods(self):
        """Test different authentication methods"""
        print("🔐 Testing Authentication Methods")
        print("=" * 50)
        
        methods_results = {}
        
        # Method 1: Token-based authentication
        print("1. Testing Bearer Token authentication...")
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            response = requests.get(f"{self.api_base_url}/v1/data", headers=headers, timeout=10)
            methods_results['bearer_token'] = {
                'status_code': response.status_code,
                'success': response.status_code < 400,
                'response_length': len(response.text)
            }
            print(f"   Status: {response.status_code} | Length: {len(response.text)} chars")
        except Exception as e:
            methods_results['bearer_token'] = {'error': str(e), 'success': False}
            print(f"   Error: {e}")
        
        # Method 2: API Key header
        print("2. Testing X-API-Key header...")
        try:
            headers = {'X-API-Key': self.token}
            response = requests.get(f"{self.api_base_url}/v1/data", headers=headers, timeout=10)
            methods_results['api_key_header'] = {
                'status_code': response.status_code,
                'success': response.status_code < 400,
                'response_length': len(response.text)
            }
            print(f"   Status: {response.status_code} | Length: {len(response.text)} chars")
        except Exception as e:
            methods_results['api_key_header'] = {'error': str(e), 'success': False}
            print(f"   Error: {e}")
        
        # Method 3: Basic auth with credentials
        print("3. Testing Basic Authentication...")
        try:
            response = requests.get(f"{self.docs_url}/docs/api", 
                                  auth=(self.email, self.password), timeout=10)
            methods_results['basic_auth'] = {
                'status_code': response.status_code,
                'success': response.status_code < 400,
                'response_length': len(response.text)
            }
            print(f"   Status: {response.status_code} | Length: {len(response.text)} chars")
        except Exception as e:
            methods_results['basic_auth'] = {'error': str(e), 'success': False}
            print(f"   Error: {e}")
        
        return methods_results
    
    def test_common_endpoints(self):
        """Test common API endpoints"""
        print("\n📡 Testing Common API Endpoints")
        print("=" * 50)
        
        # Common endpoints to test
        endpoints_to_test = [
            # API endpoints
            ("/v1/data", "Main data endpoint"),
            ("/v1/datasets", "Available datasets"),
            ("/v1/search", "Search functionality"),
            ("/v1/companies", "Company data"),
            ("/v1/people", "People data"),
            ("/api/data", "Alternative data endpoint"),
            ("/api/search", "Alternative search endpoint"),
            
            # Documentation endpoints
            ("/docs/api", "API documentation"),
            ("/docs/intro", "Introduction documentation"),
            ("/docs/api-reference", "API reference"),
        ]
        
        results = {}
        
        for endpoint, description in endpoints_to_test:
            print(f"\nTesting: {endpoint} ({description})")
            
            # Try with API base URL first
            for base_url in [self.api_base_url, self.docs_url]:
                try:
                    url = f"{base_url}{endpoint}"
                    response = self.session.get(url, timeout=10)
                    
                    result = {
                        'url': url,
                        'status_code': response.status_code,
                        'content_type': response.headers.get('content-type', 'unknown'),
                        'content_length': len(response.text),
                        'success': response.status_code < 400
                    }
                    
                    # Try to parse JSON if possible
                    if 'application/json' in result['content_type']:
                        try:
                            json_data = response.json()
                            result['json_keys'] = list(json_data.keys()) if isinstance(json_data, dict) else 'array'
                        except:
                            result['json_keys'] = 'invalid_json'
                    
                    results[f"{endpoint}_{base_url.split('//')[1].split('.')[0]}"] = result
                    
                    print(f"   ✅ {base_url}: {response.status_code} | {result['content_type']} | {result['content_length']} chars")
                    
                    if result['success']:
                        break  # Found working endpoint, no need to try other base URL
                        
                except Exception as e:
                    results[f"{endpoint}_{base_url.split('//')[1].split('.')[0]}"] = {
                        'url': f"{base_url}{endpoint}",
                        'error': str(e),
                        'success': False
                    }
                    print(f"   ❌ {base_url}: {e}")
        
        return results
    
    def test_data_fetching_with_params(self):
        """Test data fetching with various parameters"""
        print("\n📊 Testing Data Fetching with Parameters")
        print("=" * 50)
        
        test_params = [
            {'limit': 10},
            {'format': 'json'},
            {'page': 1, 'per_page': 5},
            {'search': 'technology'},
            {'category': 'companies'},
        ]
        
        results = {}
        
        for i, params in enumerate(test_params, 1):
            print(f"\n{i}. Testing with parameters: {params}")
            
            try:
                # Try both base URLs with parameters
                for base_url, endpoint in [(self.api_base_url, '/v1/data'), (self.docs_url, '/api/data')]:
                    url = f"{base_url}{endpoint}"
                    response = self.session.get(url, params=params, timeout=10)
                    
                    key = f"params_test_{i}_{base_url.split('//')[1].split('.')[0]}"
                    results[key] = {
                        'params': params,
                        'url': url,
                        'status_code': response.status_code,
                        'content_length': len(response.text),
                        'success': response.status_code < 400
                    }
                    
                    print(f"   {base_url}: {response.status_code} | {len(response.text)} chars")
                    
                    if results[key]['success']:
                        # Try to extract some sample data
                        if 'json' in response.headers.get('content-type', ''):
                            try:
                                data = response.json()
                                results[key]['sample_data'] = str(data)[:200] + "..." if len(str(data)) > 200 else str(data)
                            except:
                                pass
                        break
                        
            except Exception as e:
                print(f"   Error with params {params}: {e}")
        
        return results
    
    def generate_report(self, auth_results, endpoint_results, params_results):
        """Generate comprehensive test report"""
        print("\n📋 Comprehensive Test Report")
        print("=" * 60)
        
        # Authentication Summary
        print("\n🔐 Authentication Methods:")
        successful_auth = []
        for method, result in auth_results.items():
            status = "✅ SUCCESS" if result.get('success') else "❌ FAILED"
            print(f"   {method}: {status}")
            if result.get('success'):
                successful_auth.append(method)
        
        # Endpoints Summary
        print(f"\n📡 Endpoint Testing:")
        successful_endpoints = []
        for endpoint, result in endpoint_results.items():
            if result.get('success'):
                successful_endpoints.append(endpoint)
                print(f"   ✅ {endpoint}: {result.get('status_code')} | {result.get('content_type', 'unknown')}")
        
        failed_endpoints = [k for k, v in endpoint_results.items() if not v.get('success')]
        if failed_endpoints:
            print(f"\n   Failed endpoints: {len(failed_endpoints)}")
            for endpoint in failed_endpoints[:5]:  # Show first 5 failed
                result = endpoint_results[endpoint]
                print(f"   ❌ {endpoint}: {result.get('status_code', 'error')}")
        
        # Parameters Summary
        print(f"\n📊 Parameter Testing:")
        successful_params = [k for k, v in params_results.items() if v.get('success')]
        print(f"   Successful parameter tests: {len(successful_params)}")
        
        # Overall Summary
        print(f"\n📈 Overall Results:")
        print(f"   ✅ Working authentication methods: {len(successful_auth)}")
        print(f"   ✅ Working endpoints: {len(successful_endpoints)}")
        print(f"   ✅ Parameter tests passed: {len(successful_params)}")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        if successful_auth:
            print(f"   - Use {successful_auth[0]} for authentication")
        if successful_endpoints:
            print(f"   - Start with endpoint: {successful_endpoints[0]}")
        else:
            print("   - Check API documentation for correct endpoints")
        
        return {
            'auth_methods': len(successful_auth),
            'working_endpoints': len(successful_endpoints),
            'successful_params': len(successful_params),
            'recommendations': successful_auth[:1] + successful_endpoints[:1]
        }

def main():
    """Run comprehensive API tests"""
    print("🚀 Crust Data API Comprehensive Testing")
    print("🔑 Using token: " + os.getenv('CRUST_API_TOKEN', 'NOT_FOUND')[:20] + "...")
    print("=" * 60)
    
    tester = CrustAPITester()
    
    # Run all tests
    auth_results = tester.test_authentication_methods()
    endpoint_results = tester.test_common_endpoints()
    params_results = tester.test_data_fetching_with_params()
    
    # Generate final report
    summary = tester.generate_report(auth_results, endpoint_results, params_results)
    
    # Save detailed results to file
    all_results = {
        'authentication': auth_results,
        'endpoints': endpoint_results,
        'parameters': params_results,
        'summary': summary
    }
    
    with open('crust_api_test_results.json', 'w') as f:
        json.dump(all_results, f, indent=2, default=str)
    
    print(f"\n💾 Detailed results saved to: crust_api_test_results.json")
    print(f"✅ Testing completed!")

if __name__ == "__main__":
    main()