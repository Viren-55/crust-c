/**
 * API service for communicating with the POC Outreach Workflow backend
 */

const API_BASE_URL = 'http://localhost:8000';

export interface ICP {
  industries: string[];
  revenue_min: number;
  revenue_max: number;
  headcount_min: number;
  headcount_max: number;
}

export interface CompanyResult {
  name: string;
  domain: string;
  headcount: number;
  revenue: number;
  headquarters: string | null;
  score: number;
  industries: string[];
  founded_year: string | null;
}

export interface SearchResponse {
  companies: CompanyResult[];
  total_found: number;
  search_time_ms: number;
  icp: ICP;
}

/**
 * Search for companies based on ICP criteria
 */
export async function searchCompanies(icp: ICP): Promise<SearchResponse> {
  const response = await fetch(`${API_BASE_URL}/search-companies`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(icp),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }

  return response.json();
}

/**
 * Get available industries for ICP selection
 */
export async function getAvailableIndustries(): Promise<string[]> {
  const response = await fetch(`${API_BASE_URL}/industries`);
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data = await response.json();
  return data.industries;
}

/**
 * Get detailed company information
 */
export async function getCompanyDetails(domain: string): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/company/${domain}`);
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }

  return response.json();
}

/**
 * Health check
 */
export async function healthCheck(): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/health`);
  return response.json();
}