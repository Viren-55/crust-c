# Crust Data AI Agents Project Reference

## Overview
This reference guide provides everything you need to build AI agent projects using Crust Data APIs. Crust Data offers comprehensive data infrastructure and APIs for building intelligent applications.

## Quick Start

### Prerequisites
- Python 3.8+
- API credentials (email/password)
- Virtual environment (recommended)

### Setup
```bash
# Clone or create project directory
mkdir crust-ai-agent && cd crust-ai-agent

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install requests python-dotenv openai anthropic langchain
```

### Environment Configuration
Create `.env` file:
```env
# Crust Data API Credentials
CRUST_EMAIL=your-email@example.com
CRUST_PASSWORD=your-password
CRUST_API_BASE_URL=https://fulldocs.crustdata.com

# AI Model API Keys (choose one or more)
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
```

## Core Architecture for AI Agents

### 1. Data Layer (Crust Data Integration)
```python
import os
import requests
from typing import Dict, List, Optional
import json

class CrustDataClient:
    """Crust Data API client for AI agents"""
    
    def __init__(self):
        self.base_url = os.getenv('CRUST_API_BASE_URL')
        self.email = os.getenv('CRUST_EMAIL')
        self.password = os.getenv('CRUST_PASSWORD')
        self.session = requests.Session()
        self.authenticated = False
        
    def authenticate(self) -> bool:
        """Authenticate with Crust Data APIs"""
        try:
            # Try different authentication methods
            auth_methods = [
                self._try_basic_auth,
                self._try_api_key_auth,
                self._try_token_auth
            ]
            
            for method in auth_methods:
                if method():
                    self.authenticated = True
                    return True
            return False
        except Exception as e:
            print(f"Authentication failed: {e}")
            return False
    
    def _try_basic_auth(self) -> bool:
        """Try basic authentication"""
        self.session.auth = (self.email, self.password)
        response = self.session.get(f"{self.base_url}/docs/api")
        return response.status_code != 401
    
    def _try_api_key_auth(self) -> bool:
        """Try API key authentication"""
        headers = {
            'Authorization': f'Bearer {self.password}',
            'X-API-Key': self.password
        }
        self.session.headers.update(headers)
        response = self.session.get(f"{self.base_url}/docs/api")
        return response.status_code == 200
    
    def _try_token_auth(self) -> bool:
        """Try token-based authentication"""
        login_data = {
            'email': self.email,
            'password': self.password
        }
        
        # Try common login endpoints
        login_urls = [
            f"{self.base_url}/api/auth/login",
            f"{self.base_url}/auth/login",
            f"{self.base_url}/login"
        ]
        
        for url in login_urls:
            try:
                response = self.session.post(url, json=login_data)
                if response.status_code == 200:
                    token = response.json().get('token') or response.json().get('access_token')
                    if token:
                        self.session.headers.update({'Authorization': f'Bearer {token}'})
                        return True
            except:
                continue
        return False
    
    def get_data(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Fetch data from Crust APIs"""
        if not self.authenticated:
            if not self.authenticate():
                raise Exception("Failed to authenticate with Crust Data")
        
        try:
            response = self.session.get(f"{self.base_url}/{endpoint}", params=params)
            response.raise_for_status()
            
            # Handle different content types
            if 'application/json' in response.headers.get('content-type', ''):
                return response.json()
            else:
                return {'content': response.text, 'type': 'text'}
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            return None
    
    def search_data(self, query: str, filters: Optional[Dict] = None) -> List[Dict]:
        """Search data using Crust APIs"""
        search_params = {'q': query}
        if filters:
            search_params.update(filters)
        
        result = self.get_data('api/search', search_params)
        return result.get('results', []) if result else []
    
    def get_datasets(self) -> List[Dict]:
        """Get available datasets"""
        result = self.get_data('api/datasets')
        return result.get('datasets', []) if result else []
```

### 2. AI Agent Base Class
```python
from abc import ABC, abstractmethod
from typing import Any, Dict, List
import openai
import anthropic

class BaseAIAgent(ABC):
    """Base class for AI agents using Crust Data"""
    
    def __init__(self, name: str, model_provider: str = 'openai'):
        self.name = name
        self.model_provider = model_provider
        self.crust_client = CrustDataClient()
        self.conversation_history = []
        
        # Initialize AI model client
        if model_provider == 'openai':
            self.ai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        elif model_provider == 'anthropic':
            self.ai_client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        else:
            raise ValueError(f"Unsupported model provider: {model_provider}")
    
    @abstractmethod
    def process_query(self, query: str) -> str:
        """Process user query and return response"""
        pass
    
    def fetch_context_data(self, query: str) -> Dict:
        """Fetch relevant data from Crust APIs based on query"""
        # Search for relevant data
        search_results = self.crust_client.search_data(query)
        
        # Get additional context from specific endpoints
        context_data = {
            'search_results': search_results[:5],  # Limit results
            'datasets': self.crust_client.get_datasets()[:3],
            'query': query
        }
        
        return context_data
    
    def generate_response(self, query: str, context: Dict) -> str:
        """Generate AI response using context data"""
        system_prompt = f"""
        You are {self.name}, an AI agent with access to Crust Data APIs.
        
        Use the following context data to answer the user's query:
        - Search Results: {context.get('search_results', [])}
        - Available Datasets: {context.get('datasets', [])}
        
        Provide accurate, helpful responses based on the available data.
        """
        
        if self.model_provider == 'openai':
            response = self.ai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message.content
        
        elif self.model_provider == 'anthropic':
            response = self.ai_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=500,
                system=system_prompt,
                messages=[{"role": "user", "content": query}]
            )
            return response.content[0].text
```

### 3. Specialized AI Agents

#### Data Analysis Agent
```python
class DataAnalysisAgent(BaseAIAgent):
    """AI agent specialized in data analysis using Crust Data"""
    
    def __init__(self):
        super().__init__("Data Analyst", "openai")
    
    def process_query(self, query: str) -> str:
        """Process data analysis queries"""
        # Fetch relevant data
        context = self.fetch_context_data(query)
        
        # Add analysis-specific context
        analysis_context = {
            **context,
            'analysis_type': self._determine_analysis_type(query),
            'available_tools': ['statistics', 'visualization', 'trends', 'correlations']
        }
        
        return self.generate_response(query, analysis_context)
    
    def _determine_analysis_type(self, query: str) -> str:
        """Determine type of analysis needed"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['trend', 'over time', 'growth']):
            return 'trend_analysis'
        elif any(word in query_lower for word in ['compare', 'vs', 'difference']):
            return 'comparative_analysis'
        elif any(word in query_lower for word in ['predict', 'forecast', 'future']):
            return 'predictive_analysis'
        else:
            return 'descriptive_analysis'
```

#### Research Assistant Agent
```python
class ResearchAssistantAgent(BaseAIAgent):
    """AI agent for research tasks using Crust Data"""
    
    def __init__(self):
        super().__init__("Research Assistant", "anthropic")
    
    def process_query(self, query: str) -> str:
        """Process research queries"""
        # Multi-step research process
        research_context = self._conduct_research(query)
        return self.generate_response(query, research_context)
    
    def _conduct_research(self, query: str) -> Dict:
        """Conduct comprehensive research"""
        # Step 1: Initial data gathering
        primary_data = self.fetch_context_data(query)
        
        # Step 2: Follow-up searches based on initial results
        follow_up_queries = self._generate_follow_up_queries(query, primary_data)
        
        additional_data = []
        for follow_up in follow_up_queries[:3]:  # Limit follow-ups
            data = self.crust_client.search_data(follow_up)
            additional_data.extend(data)
        
        return {
            **primary_data,
            'additional_research': additional_data,
            'research_depth': 'comprehensive'
        }
    
    def _generate_follow_up_queries(self, original_query: str, initial_data: Dict) -> List[str]:
        """Generate follow-up research queries"""
        # This would use AI to generate relevant follow-up questions
        # based on initial results
        return [
            f"related data to {original_query}",
            f"background information {original_query}",
            f"recent developments {original_query}"
        ]
```

### 4. Agent Manager and Orchestration
```python
class AgentManager:
    """Manage multiple AI agents and route queries"""
    
    def __init__(self):
        self.agents = {
            'data_analyst': DataAnalysisAgent(),
            'research_assistant': ResearchAssistantAgent(),
        }
        self.default_agent = 'research_assistant'
    
    def route_query(self, query: str, agent_type: Optional[str] = None) -> str:
        """Route query to appropriate agent"""
        if agent_type and agent_type in self.agents:
            return self.agents[agent_type].process_query(query)
        
        # Auto-route based on query content
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['analyze', 'statistics', 'numbers', 'data']):
            return self.agents['data_analyst'].process_query(query)
        else:
            return self.agents[self.default_agent].process_query(query)
    
    def add_agent(self, name: str, agent: BaseAIAgent):
        """Add new agent to the manager"""
        self.agents[name] = agent
```

## Example Usage

### Basic Implementation
```python
# main.py
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    # Initialize agent manager
    manager = AgentManager()
    
    # Example queries
    queries = [
        "What are the latest trends in e-commerce data?",
        "Analyze the performance metrics from our dataset",
        "Find research papers related to machine learning",
        "Compare Q1 vs Q2 sales data"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        response = manager.route_query(query)
        print(f"Response: {response}")
        print("-" * 50)

if __name__ == "__main__":
    main()
```

### Advanced Multi-Agent System
```python
class MultiAgentSystem:
    """Advanced system with agent collaboration"""
    
    def __init__(self):
        self.manager = AgentManager()
        self.task_queue = []
        self.results_cache = {}
    
    def process_complex_query(self, query: str) -> Dict:
        """Process complex queries requiring multiple agents"""
        # Break down complex query into subtasks
        subtasks = self._decompose_query(query)
        
        results = {}
        for subtask in subtasks:
            agent_type = self._select_best_agent(subtask)
            result = self.manager.route_query(subtask, agent_type)
            results[subtask] = result
        
        # Synthesize results
        final_response = self._synthesize_results(query, results)
        
        return {
            'query': query,
            'subtasks': subtasks,
            'individual_results': results,
            'final_response': final_response
        }
    
    def _decompose_query(self, query: str) -> List[str]:
        """Break complex query into manageable subtasks"""
        # This would use AI to intelligently break down queries
        return [query]  # Simplified for example
    
    def _select_best_agent(self, subtask: str) -> str:
        """Select the most suitable agent for a subtask"""
        # Logic to determine best agent based on subtask characteristics
        return 'research_assistant'
    
    def _synthesize_results(self, original_query: str, results: Dict) -> str:
        """Combine results from multiple agents"""
        # Use AI to create coherent response from multiple agent outputs
        combined_results = " ".join(results.values())
        return f"Based on analysis: {combined_results}"
```

## Best Practices

### 1. Error Handling and Resilience
```python
import time
import random
from functools import wraps

def retry_with_backoff(max_retries: int = 3, backoff_factor: float = 1.0):
    """Decorator for retrying failed API calls with exponential backoff"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    
                    wait_time = backoff_factor * (2 ** attempt) + random.uniform(0, 1)
                    time.sleep(wait_time)
                    print(f"Retrying {func.__name__} after {wait_time:.2f}s (attempt {attempt + 1})")
            
        return wrapper
    return decorator

# Apply to API methods
class RobustCrustDataClient(CrustDataClient):
    @retry_with_backoff(max_retries=3)
    def get_data(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        return super().get_data(endpoint, params)
```

### 2. Caching and Performance
```python
from functools import lru_cache
import hashlib
import json

class CachedCrustDataClient(CrustDataClient):
    def __init__(self, cache_size: int = 128):
        super().__init__()
        self.cache_size = cache_size
    
    @lru_cache(maxsize=128)
    def _cached_get_data(self, endpoint: str, params_hash: str) -> Optional[Dict]:
        """Cached version of get_data"""
        params = json.loads(params_hash) if params_hash != 'None' else None
        return super().get_data(endpoint, params)
    
    def get_data(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Get data with caching"""
        params_hash = json.dumps(params, sort_keys=True) if params else 'None'
        return self._cached_get_data(endpoint, params_hash)
```

### 3. Security and Configuration
```python
import secrets
from cryptography.fernet import Fernet

class SecureConfig:
    """Secure configuration management"""
    
    def __init__(self):
        self.encryption_key = os.getenv('ENCRYPTION_KEY') or Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)
    
    def encrypt_credentials(self, credentials: Dict) -> str:
        """Encrypt sensitive credentials"""
        data = json.dumps(credentials).encode()
        return self.cipher.encrypt(data).decode()
    
    def decrypt_credentials(self, encrypted_data: str) -> Dict:
        """Decrypt credentials"""
        decrypted = self.cipher.decrypt(encrypted_data.encode())
        return json.loads(decrypted.decode())
```

### 4. Monitoring and Logging
```python
import logging
from datetime import datetime

class AgentLogger:
    """Centralized logging for AI agents"""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.logger = logging.getLogger(f"agent.{agent_name}")
        self.logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def log_query(self, query: str, response_length: int, processing_time: float):
        """Log query processing metrics"""
        self.logger.info(
            f"Processed query: {query[:50]}... | "
            f"Response length: {response_length} | "
            f"Processing time: {processing_time:.2f}s"
        )
    
    def log_api_call(self, endpoint: str, status: str, response_time: float):
        """Log API call metrics"""
        self.logger.info(
            f"API Call: {endpoint} | Status: {status} | "
            f"Response time: {response_time:.2f}s"
        )
```

## Project Structure
```
crust-ai-agent/
├── .env                          # Environment variables
├── .gitignore                    # Git ignore file
├── requirements.txt              # Python dependencies
├── README.md                     # Project documentation
├── main.py                       # Main application entry point
├── config/
│   ├── __init__.py
│   ├── settings.py               # Configuration management
│   └── logging.conf              # Logging configuration
├── agents/
│   ├── __init__.py
│   ├── base_agent.py             # Base agent class
│   ├── data_analyst.py           # Data analysis agent
│   ├── research_assistant.py     # Research agent
│   └── manager.py                # Agent manager
├── clients/
│   ├── __init__.py
│   ├── crust_client.py           # Crust Data API client
│   └── ai_models.py              # AI model integrations
├── utils/
│   ├── __init__.py
│   ├── caching.py                # Caching utilities
│   ├── security.py               # Security utilities
│   └── monitoring.py             # Monitoring and logging
├── tests/
│   ├── __init__.py
│   ├── test_agents.py            # Agent tests
│   └── test_clients.py           # Client tests
└── docs/
    ├── api_reference.md          # API documentation
    └── deployment.md             # Deployment guide
```

## Next Steps

1. **Set up authentication** with Crust Data APIs
2. **Explore available endpoints** and data structures
3. **Implement basic agent** following the examples above
4. **Test with sample queries** to validate functionality
5. **Scale and customize** based on your specific use case

## Additional Resources

- Crust Data Documentation: https://fulldocs.crustdata.com/docs/intro
- OpenAI API: https://platform.openai.com/docs
- Anthropic Claude API: https://docs.anthropic.com/
- LangChain Documentation: https://python.langchain.com/

This reference provides a solid foundation for building sophisticated AI agents that leverage Crust Data's powerful APIs for data-driven intelligence.