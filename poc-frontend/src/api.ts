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

export interface DecisionMaker {
  name: string;
  title: string;
  linkedin_profile_url?: string;
  flagship_profile_url?: string;
  email?: string;
  location?: string;
  headline?: string;
  profile_picture_url?: string;
  company_name?: string;
  is_decision_maker: boolean;
}

export interface PeopleResponse {
  decision_makers: DecisionMaker[];
  company_name: string;
  company_domain: string;
  total_found: number;
}

export interface EmailRequest {
  recipient_email: string;
  recipient_name: string;
  recipient_title: string;
  company_name: string;
  linkedin_profile_url?: string;
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
 * Get decision makers for a company
 */
export async function getCompanyDecisionMakers(domain: string, companyName?: string): Promise<PeopleResponse> {
  const url = new URL(`${API_BASE_URL}/company/${domain}/people`);
  if (companyName) {
    url.searchParams.append('company_name', companyName);
  }
  
  const response = await fetch(url.toString());
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }

  return response.json();
}

/**
 * Send personalized email to a decision maker
 */
export async function sendPersonalizedEmail(emailRequest: EmailRequest): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/send-email`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(emailRequest),
  });

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