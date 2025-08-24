# 🎯 Simplified POC Start Plan

## 🚀 **Start Here: ICP → Company Discovery → Ranking**

Let's build the **core value loop** first: Define ICP → Get companies from Crust → Rank them → Show results

---

## 📋 **Module 1: ICP + Company Discovery (TODAY)**

### **What We're Building**
```
User Input (ICP) → Crust Data Search → Company Scoring → Ranked Results
```

### **Priority Order**

#### **Step 1: Backend Foundation (2-3 hours)**
```bash
✅ Setup FastAPI project
✅ Create ICP model (industry, revenue, headcount)  
✅ Integrate existing Crust Data client
✅ Basic company scoring algorithm
✅ API endpoint: POST /search-companies
```

#### **Step 2: Simple Frontend (2-3 hours)**  
```bash
✅ React form for ICP input
✅ Company results table
✅ Display company name, headcount, score
✅ Basic styling
```

#### **Step 3: Test & Polish (1 hour)**
```bash
✅ End-to-end test with real data
✅ Error handling
✅ Loading states
```

**Total Time: 5-7 hours for complete working demo**

---

## 🛠️ **Implementation Plan**

### **Backend Structure**
```
backend/
├── main.py              # FastAPI app
├── models.py            # ICP and Company models  
├── crust_service.py     # Crust Data integration
├── scoring.py           # Company ranking logic
└── requirements.txt     # Dependencies
```

### **Frontend Structure**  
```
frontend/
├── src/
│   ├── App.tsx          # Main app
│   ├── IcpForm.tsx      # ICP input form
│   ├── CompanyList.tsx  # Results display
│   └── api.ts           # Backend calls
└── package.json
```

---

## 💻 **Step-by-Step Implementation**

### **Backend Implementation**

#### **1. Main FastAPI App**
```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from crust_service import CrustService
from scoring import ScoringService

app = FastAPI(title="POC Outreach Workflow")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

crust_service = CrustService()
scoring_service = ScoringService()

class ICP(BaseModel):
    industries: List[str]
    revenue_min: int
    revenue_max: int
    headcount_min: int  
    headcount_max: int

class CompanyResult(BaseModel):
    name: str
    domain: str
    headcount: int
    revenue: int
    headquarters: str
    score: float
    industries: List[str]

@app.post("/search-companies", response_model=List[CompanyResult])
async def search_companies(icp: ICP):
    # 1. Get companies from Crust Data
    companies = await crust_service.find_companies(icp)
    
    # 2. Score and rank companies
    scored_companies = scoring_service.score_companies(companies, icp)
    
    # 3. Return top results
    return scored_companies[:20]  # Top 20 results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### **2. Crust Data Service**
```python
# crust_service.py
from typing import List
from crust_working_api_client import CrustDataClient

class CrustService:
    def __init__(self):
        self.client = CrustDataClient()
        
    async def find_companies(self, icp) -> List[dict]:
        # Start with industry-relevant domains
        target_domains = self._get_domains_by_industry(icp.industries)
        
        # Batch fetch company data
        companies = self.client.get_company_data(
            target_domains[:100],  # Limit to 100 for POC
            fields=[
                'company_name', 'company_website_domain',
                'headcount.linkedin_headcount',
                'estimated_revenue_lower_bound_usd', 
                'headquarters', 'taxonomy.linkedin_industries'
            ]
        )
        
        # Filter by ICP criteria
        filtered = []
        for company in companies:
            if self._matches_icp_criteria(company, icp):
                filtered.append(company)
                
        return filtered
    
    def _get_domains_by_industry(self, industries: List[str]) -> List[str]:
        """Get relevant domains based on industries"""
        industry_domains = {
            'Technology': ['google.com', 'microsoft.com', 'apple.com', 'meta.com'],
            'Software': ['salesforce.com', 'adobe.com', 'oracle.com', 'sap.com'],
            'Fintech': ['stripe.com', 'square.com', 'paypal.com', 'coinbase.com'],
            'E-commerce': ['amazon.com', 'shopify.com', 'etsy.com', 'ebay.com'],
            'SaaS': ['hubspot.com', 'slack.com', 'zoom.us', 'notion.so']
        }
        
        domains = []
        for industry in industries:
            domains.extend(industry_domains.get(industry, []))
            
        # Add more domains based on similar companies
        # This would be more sophisticated in production
        return domains
        
    def _matches_icp_criteria(self, company: dict, icp) -> bool:
        """Check if company matches ICP criteria"""
        headcount = company.get('headcount', {})
        if isinstance(headcount, dict):
            emp_count = headcount.get('linkedin_headcount', 0)
        else:
            emp_count = 0
            
        revenue = company.get('estimated_revenue_lower_bound_usd', 0)
        
        # Check headcount range
        if not (icp.headcount_min <= emp_count <= icp.headcount_max):
            return False
            
        # Check revenue range  
        if not (icp.revenue_min <= revenue <= icp.revenue_max):
            return False
            
        return True
```

#### **3. Scoring Service**
```python
# scoring.py
from typing import List

class ScoringService:
    def score_companies(self, companies: List[dict], icp) -> List[dict]:
        """Score companies based on ICP fit"""
        scored = []
        
        for company in companies:
            score = self._calculate_score(company, icp)
            
            # Convert to result format
            headcount = company.get('headcount', {})
            emp_count = headcount.get('linkedin_headcount', 0) if isinstance(headcount, dict) else 0
            
            result = {
                'name': company.get('company_name', 'Unknown'),
                'domain': company.get('company_website_domain', ''),
                'headcount': emp_count,
                'revenue': company.get('estimated_revenue_lower_bound_usd', 0),
                'headquarters': company.get('headquarters', ''),
                'score': score,
                'industries': company.get('taxonomy', {}).get('linkedin_industries', [])
            }
            scored.append(result)
        
        # Sort by score (highest first)
        return sorted(scored, key=lambda x: x['score'], reverse=True)
    
    def _calculate_score(self, company: dict, icp) -> float:
        """Calculate company fit score (0-1)"""
        score = 0.0
        
        # Industry match (40% weight)
        company_industries = company.get('taxonomy', {}).get('linkedin_industries', [])
        if any(industry in icp.industries for industry in company_industries):
            score += 0.4
        
        # Size match (30% weight)
        headcount = company.get('headcount', {})
        emp_count = headcount.get('linkedin_headcount', 0) if isinstance(headcount, dict) else 0
        
        if icp.headcount_min <= emp_count <= icp.headcount_max:
            score += 0.3
            
        # Revenue match (20% weight)
        revenue = company.get('estimated_revenue_lower_bound_usd', 0)
        if icp.revenue_min <= revenue <= icp.revenue_max:
            score += 0.2
            
        # Bonus for exact industry match (10% weight)
        if any(industry.lower() in [i.lower() for i in icp.industries] 
               for industry in company_industries):
            score += 0.1
            
        return min(score, 1.0)
```

---

### **Frontend Implementation**

#### **1. Main App Component**
```typescript
// src/App.tsx
import React, { useState } from 'react';
import IcpForm from './IcpForm';
import CompanyList from './CompanyList';
import { searchCompanies } from './api';

interface ICP {
  industries: string[];
  revenue_min: number;
  revenue_max: number;
  headcount_min: number;
  headcount_max: number;
}

interface Company {
  name: string;
  domain: string;
  headcount: number;
  revenue: number;
  headquarters: string;
  score: number;
  industries: string[];
}

function App() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');

  const handleSearch = async (icp: ICP) => {
    setLoading(true);
    setError('');
    
    try {
      const results = await searchCompanies(icp);
      setCompanies(results);
    } catch (err) {
      setError('Failed to search companies. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-center mb-8">
          🎯 POC Outreach Workflow
        </h1>
        
        <div className="max-w-4xl mx-auto">
          <IcpForm onSearch={handleSearch} loading={loading} />
          
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}
          
          <CompanyList companies={companies} loading={loading} />
        </div>
      </div>
    </div>
  );
}

export default App;
```

#### **2. ICP Form Component**
```typescript  
// src/IcpForm.tsx
import React, { useState } from 'react';

interface ICP {
  industries: string[];
  revenue_min: number;
  revenue_max: number;
  headcount_min: number;
  headcount_max: number;
}

interface Props {
  onSearch: (icp: ICP) => void;
  loading: boolean;
}

const INDUSTRIES = [
  'Technology', 'Software', 'Fintech', 'E-commerce', 'SaaS', 
  'Healthcare', 'Manufacturing', 'Retail', 'Consulting'
];

const IcpForm: React.FC<Props> = ({ onSearch, loading }) => {
  const [icp, setIcp] = useState<ICP>({
    industries: ['Technology'],
    revenue_min: 1000000,
    revenue_max: 100000000,
    headcount_min: 50,
    headcount_max: 1000
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch(icp);
  };

  const handleIndustryChange = (industry: string, checked: boolean) => {
    if (checked) {
      setIcp(prev => ({
        ...prev,
        industries: [...prev.industries, industry]
      }));
    } else {
      setIcp(prev => ({
        ...prev,
        industries: prev.industries.filter(i => i !== industry)
      }));
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow-md mb-8">
      <h2 className="text-xl font-semibold mb-4">Define Your ICP</h2>
      
      {/* Industries */}
      <div className="mb-4">
        <label className="block text-sm font-medium mb-2">Industries</label>
        <div className="grid grid-cols-3 gap-2">
          {INDUSTRIES.map(industry => (
            <label key={industry} className="flex items-center">
              <input
                type="checkbox"
                checked={icp.industries.includes(industry)}
                onChange={(e) => handleIndustryChange(industry, e.target.checked)}
                className="mr-2"
              />
              {industry}
            </label>
          ))}
        </div>
      </div>

      {/* Revenue Range */}
      <div className="mb-4 grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-1">Min Revenue ($)</label>
          <input
            type="number"
            value={icp.revenue_min}
            onChange={(e) => setIcp(prev => ({ ...prev, revenue_min: Number(e.target.value) }))}
            className="w-full border rounded px-3 py-2"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Max Revenue ($)</label>
          <input
            type="number"
            value={icp.revenue_max}
            onChange={(e) => setIcp(prev => ({ ...prev, revenue_max: Number(e.target.value) }))}
            className="w-full border rounded px-3 py-2"
          />
        </div>
      </div>

      {/* Headcount Range */}
      <div className="mb-6 grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-1">Min Employees</label>
          <input
            type="number"
            value={icp.headcount_min}
            onChange={(e) => setIcp(prev => ({ ...prev, headcount_min: Number(e.target.value) }))}
            className="w-full border rounded px-3 py-2"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Max Employees</label>
          <input
            type="number"
            value={icp.headcount_max}
            onChange={(e) => setIcp(prev => ({ ...prev, headcount_max: Number(e.target.value) }))}
            className="w-full border rounded px-3 py-2"
          />
        </div>
      </div>

      <button
        type="submit"
        disabled={loading || icp.industries.length === 0}
        className="w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 disabled:opacity-50"
      >
        {loading ? 'Searching Companies...' : 'Find Companies'}
      </button>
    </form>
  );
};

export default IcpForm;
```

#### **3. Company List Component**
```typescript
// src/CompanyList.tsx  
import React from 'react';

interface Company {
  name: string;
  domain: string;
  headcount: number;
  revenue: number;
  headquarters: string;
  score: number;
  industries: string[];
}

interface Props {
  companies: Company[];
  loading: boolean;
}

const CompanyList: React.FC<Props> = ({ companies, loading }) => {
  if (loading) {
    return (
      <div className="text-center py-8">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p className="mt-2">Discovering companies...</p>
      </div>
    );
  }

  if (companies.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <p>No companies found. Try adjusting your ICP criteria.</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <div className="px-6 py-4 bg-gray-50 border-b">
        <h2 className="text-xl font-semibold">
          Found {companies.length} Companies
        </h2>
      </div>
      
      <div className="overflow-x-auto">
        <table className="min-w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Company
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Employees
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Revenue
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Location
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Score
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {companies.map((company, index) => (
              <tr key={index} className="hover:bg-gray-50">
                <td className="px-6 py-4">
                  <div>
                    <div className="font-medium text-gray-900">{company.name}</div>
                    <div className="text-sm text-gray-500">{company.domain}</div>
                    <div className="text-xs text-blue-600 mt-1">
                      {company.industries.slice(0, 2).join(', ')}
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 text-sm text-gray-900">
                  {company.headcount.toLocaleString()}
                </td>
                <td className="px-6 py-4 text-sm text-gray-900">
                  ${company.revenue.toLocaleString()}+
                </td>
                <td className="px-6 py-4 text-sm text-gray-500">
                  {company.headquarters || 'N/A'}
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center">
                    <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                      <div 
                        className="bg-green-600 h-2 rounded-full"
                        style={{ width: `${company.score * 100}%` }}
                      ></div>
                    </div>
                    <span className="text-sm font-medium">
                      {Math.round(company.score * 100)}%
                    </span>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default CompanyList;
```

#### **4. API Service**
```typescript
// src/api.ts
const API_BASE_URL = 'http://localhost:8000';

export interface ICP {
  industries: string[];
  revenue_min: number;
  revenue_max: number;
  headcount_min: number;
  headcount_max: number;
}

export interface Company {
  name: string;
  domain: string;
  headcount: number;
  revenue: number;
  headquarters: string;
  score: number;
  industries: string[];
}

export async function searchCompanies(icp: ICP): Promise<Company[]> {
  const response = await fetch(`${API_BASE_URL}/search-companies`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(icp),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
}
```

---

## 🚀 **Quick Start Commands**

### **Backend Setup**
```bash
# Create backend directory
mkdir poc-backend && cd poc-backend

# Copy working Crust client
cp ../crust_working_api_client.py .

# Create requirements.txt
echo "fastapi[all]==0.104.1
python-multipart
python-dotenv
requests" > requirements.txt

# Install dependencies
pip install -r requirements.txt

# Create the Python files above
# main.py, crust_service.py, scoring.py

# Run backend
python main.py
```

### **Frontend Setup**
```bash
# Create React app
npx create-react-app poc-frontend --template typescript
cd poc-frontend

# Install Tailwind CSS
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Create the React components above  
# src/App.tsx, src/IcpForm.tsx, src/CompanyList.tsx, src/api.ts

# Run frontend
npm start
```

---

## ✅ **Success Criteria**

**Today's Goal**: Working demo where user can:
1. ✅ Select industries (Technology, Fintech, etc.)
2. ✅ Set revenue/headcount ranges  
3. ✅ Click "Find Companies"
4. ✅ See scored, ranked companies from Crust Data
5. ✅ View company details (name, employees, revenue, score)

**Demo Flow**: `ICP Form → API Call → Crust Data → Scoring → Results Table`

**Time Estimate**: 5-7 hours for complete working system

**Ready to start coding immediately!** 🚀