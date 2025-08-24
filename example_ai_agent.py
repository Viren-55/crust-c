#!/usr/bin/env python3
"""
Example AI Agent implementation using Crust Data APIs
This is a working example based on the reference guide
"""

import os
import requests
import json
from typing import Dict, List, Optional
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

class CrustDataClient:
    """Simple Crust Data API client for AI agents"""
    
    def __init__(self):
        self.base_url = os.getenv('CRUST_DOCS_URL', 'https://fulldocs.crustdata.com')
        self.email = os.getenv('CRUST_EMAIL')
        self.password = os.getenv('CRUST_PASSWORD')
        self.session = requests.Session()
        self.authenticated = False
        
    def authenticate(self) -> bool:
        """Authenticate with Crust Data APIs"""
        if not self.email or not self.password:
            print("❌ Missing credentials in .env file")
            return False
            
        try:
            # Try basic authentication first
            self.session.auth = (self.email, self.password)
            response = self.session.get(f"{self.base_url}/docs/api")
            
            if response.status_code != 401:
                print("✅ Successfully authenticated with Crust Data")
                self.authenticated = True
                return True
            else:
                print("❌ Authentication failed")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection error: {e}")
            return False
    
    def get_documentation(self, path: str) -> Optional[str]:
        """Fetch documentation from Crust Data"""
        if not self.authenticated:
            if not self.authenticate():
                return None
        
        try:
            url = f"{self.base_url}{path}"
            response = self.session.get(url)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {path}: {e}")
            return None
    
    def extract_data_insights(self, content: str) -> Dict:
        """Extract insights from documentation content"""
        # Simple text analysis - in real implementation, you'd use NLP
        insights = {
            'content_length': len(content),
            'has_api_references': 'api' in content.lower(),
            'has_code_examples': any(term in content.lower() for term in ['example', 'code', 'curl']),
            'complexity_score': len(content.split()) / 1000,  # Simple complexity metric
            'timestamp': time.time()
        }
        return insights

class SimpleAIAgent:
    """Simple AI Agent that uses Crust Data for context"""
    
    def __init__(self, name: str):
        self.name = name
        self.crust_client = CrustDataClient()
        self.knowledge_base = {}
        
    def initialize(self) -> bool:
        """Initialize the agent"""
        print(f"🤖 Initializing {self.name}...")
        
        if not self.crust_client.authenticate():
            return False
        
        # Build initial knowledge base from Crust documentation
        print("📚 Building knowledge base...")
        docs_to_fetch = [
            '/docs/intro',
            '/docs/api',
            '/docs/developer-guide',
            '/docs/api-reference'
        ]
        
        for doc_path in docs_to_fetch:
            print(f"   Fetching {doc_path}...")
            content = self.crust_client.get_documentation(doc_path)
            if content:
                insights = self.crust_client.extract_data_insights(content)
                self.knowledge_base[doc_path] = {
                    'content': content[:1000],  # Store first 1000 chars for context
                    'insights': insights
                }
                print(f"   ✅ Added {doc_path} to knowledge base")
            else:
                print(f"   ❌ Failed to fetch {doc_path}")
        
        print(f"✅ {self.name} initialized with {len(self.knowledge_base)} knowledge sources")
        return True
    
    def process_query(self, query: str) -> str:
        """Process user query with Crust Data context"""
        print(f"\n🔍 Processing query: {query}")
        
        # Find relevant context from knowledge base
        relevant_context = self._find_relevant_context(query)
        
        # Generate response based on available context
        response = self._generate_contextual_response(query, relevant_context)
        
        return response
    
    def _find_relevant_context(self, query: str) -> Dict:
        """Find relevant information from knowledge base"""
        query_lower = query.lower()
        relevant = {}
        
        for path, data in self.knowledge_base.items():
            # Simple keyword matching
            content_lower = data['content'].lower()
            
            # Score relevance based on keyword matches
            relevance_score = 0
            for word in query_lower.split():
                if len(word) > 2:  # Skip very short words
                    relevance_score += content_lower.count(word)
            
            if relevance_score > 0:
                relevant[path] = {
                    'score': relevance_score,
                    'insights': data['insights'],
                    'snippet': data['content'][:200]
                }
        
        return relevant
    
    def _generate_contextual_response(self, query: str, context: Dict) -> str:
        """Generate response using available context"""
        if not context:
            return f"I don't have specific information about '{query}' in my current knowledge base. I have access to Crust Data documentation covering API references, developer guides, and introductory materials."
        
        # Build response based on context
        response_parts = [f"Based on Crust Data documentation, here's what I found about '{query}':\n"]
        
        # Sort by relevance score
        sorted_context = sorted(context.items(), key=lambda x: x[1]['score'], reverse=True)
        
        for path, data in sorted_context[:2]:  # Top 2 most relevant
            response_parts.append(f"\n📄 From {path}:")
            response_parts.append(f"   - Relevance score: {data['score']}")
            response_parts.append(f"   - Content complexity: {data['insights']['complexity_score']:.1f}")
            response_parts.append(f"   - Snippet: {data['snippet']}...")
        
        response_parts.append(f"\n💡 I found {len(context)} relevant sources in total.")
        response_parts.append("For more detailed information, I can fetch specific documentation sections.")
        
        return "\n".join(response_parts)
    
    def get_status(self) -> Dict:
        """Get agent status and statistics"""
        return {
            'name': self.name,
            'authenticated': self.crust_client.authenticated,
            'knowledge_base_size': len(self.knowledge_base),
            'available_sources': list(self.knowledge_base.keys())
        }

def main():
    """Example usage of the AI Agent"""
    print("🚀 Starting Crust Data AI Agent Example")
    print("=" * 50)
    
    # Create and initialize agent
    agent = SimpleAIAgent("Crust Assistant")
    
    if not agent.initialize():
        print("❌ Failed to initialize agent")
        return
    
    # Show agent status
    status = agent.get_status()
    print(f"\n📊 Agent Status:")
    print(f"   Name: {status['name']}")
    print(f"   Authenticated: {status['authenticated']}")
    print(f"   Knowledge sources: {status['knowledge_base_size']}")
    print(f"   Available sources: {', '.join(status['available_sources'])}")
    
    # Example queries
    example_queries = [
        "What is Crust Data?",
        "How do I use the API?",
        "What are the authentication methods?",
        "Tell me about data analysis features",
        "How do I get started with development?"
    ]
    
    print(f"\n🎯 Running example queries...")
    print("=" * 50)
    
    for i, query in enumerate(example_queries, 1):
        print(f"\n--- Query {i} ---")
        response = agent.process_query(query)
        print(response)
        print("-" * 40)
        
        # Small delay between queries
        time.sleep(1)
    
    print("\n✅ Example completed!")
    print("\nNext steps:")
    print("1. Customize the agent for your specific use case")
    print("2. Add more sophisticated NLP for better context matching")
    print("3. Integrate with actual AI models (OpenAI, Anthropic, etc.)")
    print("4. Add persistent storage for knowledge base")
    print("5. Implement real-time data updates")

if __name__ == "__main__":
    main()