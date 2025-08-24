#!/usr/bin/env python3
"""
Working AI Agent with Crust Data Integration
This agent uses the verified working Crust Data API endpoints
"""

import os
import json
from typing import Dict, List, Optional, Any
from crust_working_api_client import CrustDataClient
from dotenv import load_dotenv
import re
from datetime import datetime

load_dotenv()

class CrustDataAIAgent:
    """
    AI Agent that leverages Crust Data APIs for company intelligence
    
    This agent can:
    - Enrich company data from domains
    - Perform competitive analysis
    - Answer business intelligence queries
    - Provide market insights
    """
    
    def __init__(self, name: str = "Crust Business Intelligence Agent"):
        self.name = name
        self.crust_client = CrustDataClient()
        self.knowledge_cache = {}  # Simple caching
        
        print(f"🤖 {self.name} initialized successfully!")
        print(f"   ✅ Crust Data API connected")
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process natural language business queries using Crust Data
        
        Args:
            query: Natural language query about companies/business
            
        Returns:
            Structured response with data and insights
        """
        print(f"\n🔍 Processing query: '{query}'")
        
        # Parse query to determine intent and extract entities
        intent = self._analyze_query_intent(query)
        entities = self._extract_entities(query)
        
        print(f"   📊 Detected intent: {intent}")
        print(f"   🎯 Extracted entities: {entities}")
        
        # Route to appropriate handler
        if intent == 'company_lookup':
            return self._handle_company_lookup(entities, query)
        elif intent == 'competitive_analysis':
            return self._handle_competitive_analysis(entities, query)
        elif intent == 'industry_analysis':
            return self._handle_industry_analysis(entities, query)
        elif intent == 'company_comparison':
            return self._handle_company_comparison(entities, query)
        elif intent == 'market_research':
            return self._handle_market_research(entities, query)
        else:
            return self._handle_general_query(entities, query)
    
    def _analyze_query_intent(self, query: str) -> str:
        """Analyze query to determine intent"""
        query_lower = query.lower()
        
        # Company lookup patterns
        if any(pattern in query_lower for pattern in ['tell me about', 'what is', 'who is', 'company profile', 'information about']):
            return 'company_lookup'
        
        # Competitive analysis patterns
        elif any(pattern in query_lower for pattern in ['compete', 'competitor', 'vs', 'compare', 'comparison']):
            return 'competitive_analysis'
        
        # Industry analysis patterns
        elif any(pattern in query_lower for pattern in ['industry', 'market', 'sector', 'space']):
            return 'industry_analysis'
        
        # Market research patterns
        elif any(pattern in query_lower for pattern in ['trends', 'growing', 'emerging', 'leaders', 'top companies']):
            return 'market_research'
        
        # Comparison patterns
        elif any(pattern in query_lower for pattern in ['compare', 'difference', 'better', 'larger', 'smaller']):
            return 'company_comparison'
        
        else:
            return 'general_query'
    
    def _extract_entities(self, query: str) -> Dict[str, List[str]]:
        """Extract companies, domains, and other entities from query"""
        entities = {
            'domains': [],
            'companies': [],
            'industries': [],
            'metrics': []
        }
        
        # Extract domains (basic pattern)
        domain_pattern = r'([a-zA-Z0-9-]+\.(?:com|org|net|io|co|ai))'
        domains = re.findall(domain_pattern, query)
        entities['domains'].extend(domains)
        
        # Extract company names (simple patterns)
        company_patterns = [
            r'\\b(Google|Apple|Microsoft|Amazon|Facebook|Meta|Tesla|Netflix|Uber|Airbnb)\\b',
            r'\\b(Salesforce|HubSpot|Slack|Zoom|Stripe|PayPal|Square)\\b',
            r'\\b(OpenAI|Anthropic|Notion|Figma|Canva|Discord)\\b'
        ]
        
        for pattern in company_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            entities['companies'].extend([m.lower() for m in matches])
        
        # Extract industries
        industry_keywords = ['fintech', 'saas', 'ai', 'ml', 'crm', 'ecommerce', 'social media', 'cloud']
        for keyword in industry_keywords:
            if keyword in query.lower():
                entities['industries'].append(keyword)
        
        # Extract metrics
        metric_keywords = ['revenue', 'employees', 'headcount', 'funding', 'valuation', 'growth']
        for keyword in metric_keywords:
            if keyword in query.lower():
                entities['metrics'].append(keyword)
        
        return entities
    
    def _handle_company_lookup(self, entities: Dict, query: str) -> Dict:
        """Handle company profile/lookup queries"""
        response = {
            'intent': 'company_lookup',
            'query': query,
            'companies_analyzed': [],
            'insights': [],
            'data': {}
        }
        
        # Get domains to lookup
        domains = entities['domains']
        
        # Add common domain mappings for known companies
        company_domain_map = {
            'google': 'google.com',
            'apple': 'apple.com',
            'microsoft': 'microsoft.com',
            'amazon': 'amazon.com',
            'facebook': 'facebook.com',
            'meta': 'facebook.com',
            'salesforce': 'salesforce.com',
            'hubspot': 'hubspot.com',
            'slack': 'slack.com',
            'stripe': 'stripe.com',
            'openai': 'openai.com',
            'anthropic': 'anthropic.com'
        }
        
        for company in entities['companies']:
            if company in company_domain_map:
                domains.append(company_domain_map[company])
        
        if not domains:
            # Try to infer domain from query
            words = query.lower().split()
            for word in words:
                if word in company_domain_map:
                    domains.append(company_domain_map[word])
        
        if not domains:
            response['insights'].append("No specific companies identified. Please mention company domains (e.g., google.com) or known company names.")
            return response
        
        # Fetch company data
        fields = [
            'company_name', 'company_website_domain', 'headquarters',
            'year_founded', 'estimated_revenue_lower_bound_usd',
            'headcount.linkedin_headcount', 'linkedin_company_description',
            'taxonomy.linkedin_industries', 'taxonomy.crunchbase_categories'
        ]
        
        result = self.crust_client.get_company_data(domains, fields=fields)
        
        if isinstance(result, list):
            for company_data in result:
                company_name = company_data.get('company_name', 'Unknown')
                response['companies_analyzed'].append(company_name)
                response['data'][company_name] = company_data
                
                # Generate insights
                insights = self._generate_company_insights(company_data)
                response['insights'].extend(insights)
        
        return response
    
    def _handle_competitive_analysis(self, entities: Dict, query: str) -> Dict:
        """Handle competitive analysis queries"""
        response = {
            'intent': 'competitive_analysis',
            'query': query,
            'competitors': [],
            'comparison': {},
            'insights': []
        }
        
        domains = entities['domains']
        
        # If no specific domains, try to infer from context
        if not domains:
            # Look for industry context to get relevant companies
            if 'crm' in query.lower():
                domains = ['salesforce.com', 'hubspot.com', 'pipedrive.com']
            elif 'payment' in query.lower() or 'fintech' in query.lower():
                domains = ['stripe.com', 'square.com', 'paypal.com']
            elif 'ai' in query.lower():
                domains = ['openai.com', 'anthropic.com', 'huggingface.co']
        
        if len(domains) < 2:
            response['insights'].append("Competitive analysis requires at least 2 companies. Please specify company domains.")
            return response
        
        # Fetch competitive data
        fields = [
            'company_name', 'headcount.linkedin_headcount',
            'estimated_revenue_lower_bound_usd', 'year_founded',
            'headquarters', 'taxonomy.linkedin_industries'
        ]
        
        result = self.crust_client.get_company_data(domains, fields=fields)
        
        if isinstance(result, list):
            response['competitors'] = [c.get('company_name', 'Unknown') for c in result]
            
            # Create comparison table
            comparison_metrics = {}
            for company_data in result:
                name = company_data.get('company_name', 'Unknown')
                
                headcount = company_data.get('headcount', {})
                employees = headcount.get('linkedin_headcount', 0) if isinstance(headcount, dict) else 0
                
                revenue = company_data.get('estimated_revenue_lower_bound_usd', 0)
                founded = company_data.get('year_founded', '')
                hq = company_data.get('headquarters', 'Unknown')
                
                comparison_metrics[name] = {
                    'employees': employees,
                    'revenue': revenue,
                    'founded': founded,
                    'headquarters': hq,
                    'age_years': 2025 - int(founded[:4]) if founded and founded[:4].isdigit() else 0
                }
            
            response['comparison'] = comparison_metrics
            
            # Generate competitive insights
            insights = self._generate_competitive_insights(comparison_metrics)
            response['insights'].extend(insights)
        
        return response
    
    def _handle_industry_analysis(self, entities: Dict, query: str) -> Dict:
        """Handle industry analysis queries"""
        response = {
            'intent': 'industry_analysis',
            'query': query,
            'industry': entities.get('industries', ['technology'])[0] if entities.get('industries') else 'technology',
            'companies': [],
            'insights': []
        }
        
        # Get relevant companies for the industry
        industry_companies = {
            'fintech': ['stripe.com', 'square.com', 'plaid.com', 'coinbase.com', 'robinhood.com'],
            'saas': ['salesforce.com', 'hubspot.com', 'slack.com', 'notion.so', 'figma.com'],
            'ai': ['openai.com', 'anthropic.com', 'huggingface.co', 'cohere.ai'],
            'crm': ['salesforce.com', 'hubspot.com', 'pipedrive.com'],
            'social media': ['facebook.com', 'twitter.com', 'linkedin.com', 'discord.com'],
            'ecommerce': ['amazon.com', 'shopify.com', 'etsy.com']
        }
        
        industry = response['industry']
        domains = industry_companies.get(industry, ['google.com', 'microsoft.com', 'apple.com'])
        
        # Fetch industry data
        fields = [
            'company_name', 'headcount.linkedin_headcount',
            'estimated_revenue_lower_bound_usd', 'year_founded'
        ]
        
        result = self.crust_client.get_company_data(domains, fields=fields)
        
        if isinstance(result, list):
            response['companies'] = result
            
            # Generate industry insights
            insights = self._generate_industry_insights(result, industry)
            response['insights'].extend(insights)
        
        return response
    
    def _handle_company_comparison(self, entities: Dict, query: str) -> Dict:
        """Handle direct company comparison queries"""
        # Similar to competitive analysis but more focused
        return self._handle_competitive_analysis(entities, query)
    
    def _handle_market_research(self, entities: Dict, query: str) -> Dict:
        """Handle market research queries"""
        response = {
            'intent': 'market_research',
            'query': query,
            'market_data': {},
            'trends': [],
            'insights': []
        }
        
        # Define market segments
        if 'growing' in query.lower() or 'emerging' in query.lower():
            # Focus on newer, high-growth companies
            domains = ['stripe.com', 'notion.so', 'discord.com', 'figma.com', 'canva.com']
        elif 'ai' in query.lower():
            domains = ['openai.com', 'anthropic.com', 'huggingface.co', 'cohere.ai', 'replicate.com']
        elif 'fintech' in query.lower():
            domains = ['stripe.com', 'coinbase.com', 'robinhood.com', 'plaid.com', 'square.com']
        else:
            # General market leaders
            domains = ['google.com', 'microsoft.com', 'apple.com', 'amazon.com', 'salesforce.com']
        
        fields = [
            'company_name', 'headcount.linkedin_headcount',
            'estimated_revenue_lower_bound_usd', 'year_founded',
            'taxonomy.linkedin_industries'
        ]
        
        result = self.crust_client.get_company_data(domains, fields=fields)
        
        if isinstance(result, list):
            response['market_data'] = {
                'companies_analyzed': len(result),
                'total_employees': 0,
                'average_age': 0,
                'companies': result
            }
            
            # Calculate market metrics
            total_employees = 0
            ages = []
            
            for company in result:
                headcount = company.get('headcount', {})
                if isinstance(headcount, dict):
                    employees = headcount.get('linkedin_headcount', 0)
                    total_employees += employees
                
                founded = company.get('year_founded', '')
                if founded and founded[:4].isdigit():
                    age = 2025 - int(founded[:4])
                    ages.append(age)
            
            response['market_data']['total_employees'] = total_employees
            response['market_data']['average_age'] = sum(ages) / len(ages) if ages else 0
            
            # Generate market insights
            insights = self._generate_market_insights(result, query)
            response['insights'].extend(insights)
        
        return response
    
    def _handle_general_query(self, entities: Dict, query: str) -> Dict:
        """Handle general queries"""
        return {
            'intent': 'general_query',
            'query': query,
            'response': f"I can help with company data analysis. Try asking about specific companies (e.g., 'Tell me about google.com') or industry comparisons.",
            'suggestions': [
                "Tell me about stripe.com",
                "Compare salesforce.com and hubspot.com",
                "Show me fintech companies",
                "Analyze the AI industry"
            ]
        }
    
    def _generate_company_insights(self, company_data: Dict) -> List[str]:
        """Generate insights about a single company"""
        insights = []
        
        name = company_data.get('company_name', 'Company')
        
        # Employee insights
        headcount = company_data.get('headcount', {})
        if isinstance(headcount, dict):
            employees = headcount.get('linkedin_headcount', 0)
            if employees > 10000:
                insights.append(f"{name} is a large enterprise with {employees:,} employees")
            elif employees > 1000:
                insights.append(f"{name} is a mid-size company with {employees:,} employees")
            elif employees > 100:
                insights.append(f"{name} is a growing company with {employees:,} employees")
        
        # Revenue insights
        revenue = company_data.get('estimated_revenue_lower_bound_usd', 0)
        if revenue >= 1000000000:
            insights.append(f"{name} generates over $1B in estimated revenue")
        elif revenue >= 100000000:
            insights.append(f"{name} generates over $100M in estimated revenue")
        
        # Age insights
        founded = company_data.get('year_founded', '')
        if founded and founded[:4].isdigit():
            age = 2025 - int(founded[:4])
            if age < 5:
                insights.append(f"{name} is a very young company (founded {founded[:4]})")
            elif age < 15:
                insights.append(f"{name} is a relatively young company (founded {founded[:4]})")
            else:
                insights.append(f"{name} is an established company (founded {founded[:4]})")
        
        return insights
    
    def _generate_competitive_insights(self, comparison_metrics: Dict) -> List[str]:
        """Generate competitive analysis insights"""
        insights = []
        
        if not comparison_metrics:
            return insights
        
        # Find largest by employees
        largest_by_employees = max(comparison_metrics.items(), key=lambda x: x[1]['employees'])
        insights.append(f"Largest by employee count: {largest_by_employees[0]} ({largest_by_employees[1]['employees']:,} employees)")
        
        # Find highest revenue
        companies_with_revenue = {k: v for k, v in comparison_metrics.items() if v['revenue'] > 0}
        if companies_with_revenue:
            highest_revenue = max(companies_with_revenue.items(), key=lambda x: x[1]['revenue'])
            insights.append(f"Highest estimated revenue: {highest_revenue[0]} (${highest_revenue[1]['revenue']:,}+ USD)")
        
        # Find oldest company
        companies_with_age = {k: v for k, v in comparison_metrics.items() if v['age_years'] > 0}
        if companies_with_age:
            oldest = max(companies_with_age.items(), key=lambda x: x[1]['age_years'])
            insights.append(f"Most established: {oldest[0]} ({oldest[1]['age_years']} years old)")
        
        return insights
    
    def _generate_industry_insights(self, companies: List[Dict], industry: str) -> List[str]:
        """Generate industry-level insights"""
        insights = []
        
        total_employees = 0
        employee_counts = []
        
        for company in companies:
            headcount = company.get('headcount', {})
            if isinstance(headcount, dict):
                employees = headcount.get('linkedin_headcount', 0)
                total_employees += employees
                employee_counts.append(employees)
        
        if employee_counts:
            avg_employees = total_employees / len(employee_counts)
            insights.append(f"{industry.title()} industry analysis: {len(companies)} companies with {total_employees:,} total employees")
            insights.append(f"Average company size: {avg_employees:,.0f} employees")
            
            largest = max(employee_counts)
            smallest = min([e for e in employee_counts if e > 0])
            if smallest > 0:
                insights.append(f"Size range: {smallest:,} to {largest:,} employees")
        
        return insights
    
    def _generate_market_insights(self, companies: List[Dict], query: str) -> List[str]:
        """Generate market research insights"""
        insights = []
        
        # Growth indicators
        high_growth_companies = []
        
        for company in companies:
            headcount = company.get('headcount', {})
            employees = headcount.get('linkedin_headcount', 0) if isinstance(headcount, dict) else 0
            
            founded = company.get('year_founded', '')
            if founded and founded[:4].isdigit():
                age = 2025 - int(founded[:4])
                if employees > 1000 and age < 15:  # Large and young = high growth
                    high_growth_companies.append(company.get('company_name', 'Unknown'))
        
        if high_growth_companies:
            insights.append(f"High-growth companies identified: {', '.join(high_growth_companies)}")
        
        insights.append(f"Market analysis complete for {len(companies)} companies")
        
        return insights
    
    def format_response(self, response_data: Dict) -> str:
        """Format response data for display"""
        intent = response_data.get('intent', 'unknown')
        query = response_data.get('query', '')
        
        formatted = f"🤖 {self.name} Response\\n"
        formatted += f"Query: {query}\\n"
        formatted += f"Intent: {intent}\\n\\n"
        
        if intent == 'company_lookup':
            companies = response_data.get('companies_analyzed', [])
            if companies:
                formatted += f"📊 Companies Analyzed: {', '.join(companies)}\\n\\n"
                
                for company in companies:
                    data = response_data['data'].get(company, {})
                    formatted += f"🏢 {company}:\\n"
                    
                    # Key metrics
                    headcount = data.get('headcount', {})
                    if isinstance(headcount, dict):
                        employees = headcount.get('linkedin_headcount', 'Unknown')
                        formatted += f"   👥 Employees: {employees:,}\\n" if isinstance(employees, int) else f"   👥 Employees: {employees}\\n"
                    
                    hq = data.get('headquarters', 'Unknown')
                    formatted += f"   📍 Headquarters: {hq}\\n"
                    
                    founded = data.get('year_founded', 'Unknown')
                    formatted += f"   📅 Founded: {founded[:4] if founded and len(founded) >= 4 else founded}\\n"
                    
                    revenue = data.get('estimated_revenue_lower_bound_usd', 0)
                    if revenue > 0:
                        formatted += f"   💰 Est. Revenue: ${revenue:,}+ USD\\n"
                    
                    formatted += "\\n"
        
        elif intent == 'competitive_analysis':
            competitors = response_data.get('competitors', [])
            comparison = response_data.get('comparison', {})
            
            if competitors:
                formatted += f"🥊 Competitive Analysis: {', '.join(competitors)}\\n\\n"
                
                # Create comparison table
                formatted += f"{'Company':<20} {'Employees':<12} {'Founded':<10} {'HQ':<20}\\n"
                formatted += f"{'-'*70}\\n"
                
                for company, metrics in comparison.items():
                    employees = f"{metrics['employees']:,}" if metrics['employees'] > 0 else 'N/A'
                    founded = metrics['founded'][:4] if metrics['founded'] else 'N/A'
                    hq = metrics['headquarters'][:18] if metrics['headquarters'] != 'Unknown' else 'N/A'
                    
                    formatted += f"{company[:18]:<20} {employees:<12} {founded:<10} {hq:<20}\\n"
                
                formatted += "\\n"
        
        # Add insights
        insights = response_data.get('insights', [])
        if insights:
            formatted += f"💡 Key Insights:\\n"
            for insight in insights:
                formatted += f"   • {insight}\\n"
        
        return formatted

def main():
    """Test the working AI agent"""
    print("🚀 Crust Data AI Agent - Working Version")
    print("=" * 60)
    
    agent = CrustDataAIAgent()
    
    # Test queries
    test_queries = [
        "Tell me about stripe.com",
        "Compare salesforce.com and hubspot.com", 
        "Show me fintech companies",
        "What are some growing AI companies?",
        "Analyze google.com and microsoft.com"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\\n--- Test Query {i} ---")
        
        response = agent.process_query(query)
        formatted_response = agent.format_response(response)
        
        print(formatted_response)
        print("-" * 60)
    
    print("\\n✅ AI Agent testing completed successfully!")
    print("\\n💡 The agent can now:")
    print("   - Analyze company profiles from domains")
    print("   - Perform competitive analysis")
    print("   - Conduct industry research") 
    print("   - Generate business insights")
    print("   - Answer natural language business queries")

if __name__ == "__main__":
    main()