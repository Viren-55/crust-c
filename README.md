# Crust Data AI Agents Project

This project provides tools and examples for building AI agents that leverage Crust Data APIs.

## Quick Start

### 1. Setup Environment
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Credentials
Your `.env` file is already configured with Crust Data credentials.

### 3. Run Example Agent
```bash
# Run the example AI agent
python3 example_ai_agent.py

# Or use the documentation access script
python3 crust_docs_access.py
```

## Files Overview

- **`crust_ai_agents_reference.md`** - Comprehensive guide for building AI agents
- **`example_ai_agent.py`** - Working example implementation
- **`crust_docs_access.py`** - Script to access Crust documentation
- **`.env`** - Environment variables (credentials configured)
- **`requirements.txt`** - Python dependencies

## Example Usage

The example agent demonstrates:
- ✅ Authentication with Crust Data APIs
- ✅ Building a knowledge base from documentation
- ✅ Processing queries with contextual responses
- ✅ Simple relevance scoring for information retrieval

## Next Steps

1. **Customize the agent** for your specific use case
2. **Add AI model integration** (OpenAI, Anthropic, etc.)
3. **Enhance NLP capabilities** for better context understanding
4. **Implement persistent storage** for knowledge base
5. **Add real-time data updates** from Crust APIs

## Architecture

The project follows a modular architecture:
- **Data Layer** - Crust Data API integration
- **Agent Layer** - AI processing and reasoning
- **Application Layer** - User interaction and orchestration

For detailed implementation guidance, see `crust_ai_agents_reference.md`.