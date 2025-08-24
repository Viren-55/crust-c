"""
People Service for Crust Data Integration
Handles decision maker discovery using Crust People API
"""

from typing import List, Dict, Any
import asyncio
from concurrent.futures import ThreadPoolExecutor
from models import DecisionMaker
from crust_working_api_client import CrustDataClient

class PeopleService:
    def __init__(self):
        self.client = CrustDataClient()
        self.executor = ThreadPoolExecutor(max_workers=2)
    
    async def find_decision_makers(self, company_name: str, company_domain: str) -> List[DecisionMaker]:
        """Find decision makers for a specific company using People Search API"""
        
        # Build filters for decision makers at the company
        filters = self._build_people_filters(company_name, company_domain)
        
        # Fetch people data using search API (run in thread pool to avoid blocking)
        loop = asyncio.get_event_loop()
        people = await loop.run_in_executor(
            self.executor,
            self._fetch_people_by_filters,
            filters
        )
        
        # Convert to DecisionMaker objects
        decision_makers = []
        for person in people:
            decision_maker = self._convert_to_decision_maker(person, company_name)
            if decision_maker:
                decision_makers.append(decision_maker)
        
        print(f"🎯 Found {len(decision_makers)} decision makers for {company_name}")
        return decision_makers[:5]  # Limit to top 5 decision makers
    
    def _fetch_company_with_decision_makers(self, company_domain: str) -> Dict[str, Any]:
        """Fetch company data with decision makers using enrichment API"""
        try:
            print(f"🔍 Fetching company with decision makers for: {company_domain}")
            
            # Request specific fields including decision makers
            fields = [
                'company_name', 'company_domain', 'decision_makers',
                'founder_names_and_profile_urls', 'founders_location'
            ]
            
            response = self.client.get_company_data(company_domain, fields=fields)
            
            print(f"📊 Company enrichment response type: {type(response)}")
            
            if isinstance(response, list) and len(response) > 0:
                company_data = response[0]
                print(f"📊 Company data keys: {list(company_data.keys())}")
                print(f"📊 Decision makers available: {'decision_makers' in company_data}")
                return company_data
            elif isinstance(response, dict):
                print(f"📊 Direct company data keys: {list(response.keys())}")
                return response
            else:
                print(f"📊 Unexpected company response: {type(response)}")
                return {}
                
        except Exception as e:
            print(f"❌ Error fetching company with decision makers: {e}")
            return {}
    
    def _convert_company_dm_to_decision_maker(self, dm_data: Dict[str, Any], company_name: str) -> DecisionMaker:
        """Convert company decision maker data to DecisionMaker model"""
        try:
            # Extract data from company decision makers format
            decision_maker = DecisionMaker(
                name=dm_data.get('name', 'Unknown'),
                title=dm_data.get('title', ''),
                linkedin_profile_url=dm_data.get('linkedin_profile_url'),
                flagship_profile_url=dm_data.get('linkedin_flagship_url'),
                email=None,  # Not typically available in company endpoint
                location=dm_data.get('location'),
                headline=dm_data.get('headline'),
                profile_picture_url=dm_data.get('profile_picture_url'),
                company_name=company_name,
                is_decision_maker=True  # All from this endpoint are decision makers
            )
            
            print(f"📊 Converted decision maker: {decision_maker.name} - {decision_maker.title}")
            return decision_maker
            
        except Exception as e:
            print(f"❌ Error converting company DM data: {e}")
            return None
    
    def _build_people_filters(self, company_name: str, company_domain: str) -> List[Dict[str, Any]]:
        """Build filters for Crust People Search API using correct format"""
        
        # Use the correct filter structure as shown in the example
        filters = [
            {
                "filter_type": "CURRENT_COMPANY",
                "type": "in",
                "value": [company_domain, company_name]
            },
            {
                "filter_type": "CURRENT_TITLE",
                "type": "in",
                "value": [
                    "CEO", "Chief Executive Officer", "CTO", "Chief Technology Officer",
                    "CFO", "Chief Financial Officer", "CMO", "Chief Marketing Officer", 
                    "COO", "Chief Operating Officer", "President", "VP", "Vice President",
                    "Director", "Head", "Manager"
                ]
            }
        ]
        
        print(f"🔍 Built people filters for {company_name}: {filters}")
        return filters
    
    def _fetch_people_by_filters(self, filters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Fetch people using Crust People Search API with correct payload structure"""
        try:
            print(f"🔍 Calling Crust People Search API...")
            
            # Build payload for people search using exact format from example
            payload = {
                "filters": filters,
                "page": 1
            }
            
            print(f"🔍 People search payload: {payload}")
            
            # Use the people search endpoint with correct path
            response = self.client._make_request('POST', '/screener/person/search/', json=payload)
            
            print(f"📊 People API response type: {type(response)}")
            print(f"📊 People API response keys: {list(response.keys()) if isinstance(response, dict) else 'Not a dict'}")
            
            if isinstance(response, dict):
                # Check if it's an error response
                if 'error' in response:
                    print(f"❌ People API Error: {response.get('error')}")
                    return []
                
                # Extract people from response
                if 'profiles' in response:
                    profiles = response['profiles']
                    print(f"📊 Found {len(profiles)} people profiles")
                    
                    if profiles:
                        print(f"📊 Sample person keys: {list(profiles[0].keys())}")
                        print(f"📊 Sample person: {profiles[0].get('name', 'Unknown')}")
                    
                    return profiles
                else:
                    print(f"📊 Unexpected people response structure: {list(response.keys())}")
                    return []
            else:
                print(f"📊 Unexpected people response type: {type(response)}")
                return []
                
        except Exception as e:
            print(f"❌ Error calling people search API: {e}")
            return []
    
    def _convert_to_decision_maker(self, person_data: Dict[str, Any], company_name: str) -> DecisionMaker:
        """Convert Crust API person data to DecisionMaker model"""
        try:
            # Extract email from emails array
            emails = person_data.get('emails', [])
            email = emails[0] if emails else None
            
            # Check if person is in a decision-making role
            title = person_data.get('default_position_title', '') or person_data.get('current_title', '')
            is_decision_maker = person_data.get('default_position_is_decision_maker', False)
            
            # Create DecisionMaker object
            decision_maker = DecisionMaker(
                name=person_data.get('name', 'Unknown'),
                title=title,
                linkedin_profile_url=person_data.get('linkedin_profile_url'),
                flagship_profile_url=person_data.get('flagship_profile_url'),
                email=email,
                location=person_data.get('location'),
                headline=person_data.get('headline'),
                profile_picture_url=person_data.get('profile_picture_url'),
                company_name=company_name,
                is_decision_maker=is_decision_maker
            )
            
            return decision_maker
            
        except Exception as e:
            print(f"❌ Error converting person data: {e}")
            return None