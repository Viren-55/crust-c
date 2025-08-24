import React, { useState } from 'react';
import { searchCompanies, getCompanyDecisionMakers, sendPersonalizedEmail, ICP, SearchResponse, PeopleResponse, DecisionMaker } from './api';
import './index.css';

function SimpleApp() {
  const [searchResponse, setSearchResponse] = useState<SearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');
  
  // Decision makers state
  const [expandedCompanies, setExpandedCompanies] = useState<Set<string>>(new Set());
  const [companyDecisionMakers, setCompanyDecisionMakers] = useState<Record<string, PeopleResponse>>({});
  const [loadingDecisionMakers, setLoadingDecisionMakers] = useState<Set<string>>(new Set());
  const [sendingEmails, setSendingEmails] = useState<Set<string>>(new Set());
  
  // ICP Form State
  const [icp, setIcp] = useState<ICP>({
    industries: ['Technology'],
    revenue_min: 10000000,      // $10M
    revenue_max: 1000000000,    // $1B
    headcount_min: 100,
    headcount_max: 5000
  });

  const industries = [
    'Technology', 'Software', 'Fintech', 'E-commerce', 'SaaS',
    'Healthcare', 'Manufacturing', 'Retail', 'Consulting'
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      console.log('🔍 Searching with ICP:', icp);
      const response = await searchCompanies(icp);
      console.log('✅ Search response:', response);
      setSearchResponse(response);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to search companies';
      setError(errorMessage);
      console.error('❌ Search error:', err);
    } finally {
      setLoading(false);
    }
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

  const formatCurrency = (value: number) => {
    if (value >= 1000000000) {
      return `$${(value / 1000000000).toFixed(1)}B+`;
    } else if (value >= 1000000) {
      return `$${(value / 1000000).toFixed(0)}M+`;
    } else if (value > 0) {
      return `$${value.toLocaleString()}+`;
    } else {
      return 'N/A';
    }
  };

  const toggleCompanyExpansion = async (domain: string, companyName: string) => {
    const isExpanded = expandedCompanies.has(domain);
    
    if (isExpanded) {
      // Collapse the company
      const newExpandedCompanies = new Set(expandedCompanies);
      newExpandedCompanies.delete(domain);
      setExpandedCompanies(newExpandedCompanies);
    } else {
      // Expand the company and fetch decision makers if not already loaded
      const newExpandedCompanies = new Set(expandedCompanies);
      newExpandedCompanies.add(domain);
      setExpandedCompanies(newExpandedCompanies);
      
      if (!companyDecisionMakers[domain]) {
        await loadDecisionMakers(domain, companyName);
      }
    }
  };

  const loadDecisionMakers = async (domain: string, companyName: string) => {
    const newLoadingSet = new Set(loadingDecisionMakers);
    newLoadingSet.add(domain);
    setLoadingDecisionMakers(newLoadingSet);
    
    try {
      console.log(`🔍 Loading decision makers for ${companyName} (${domain})`);
      const peopleResponse = await getCompanyDecisionMakers(domain, companyName);
      
      setCompanyDecisionMakers(prev => ({
        ...prev,
        [domain]: peopleResponse
      }));
      
      console.log(`✅ Loaded ${peopleResponse.decision_makers.length} decision makers for ${companyName}`);
    } catch (err) {
      console.error(`❌ Error loading decision makers for ${companyName}:`, err);
      setError(`Failed to load decision makers for ${companyName}: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      const newLoadingSet = new Set(loadingDecisionMakers);
      newLoadingSet.delete(domain);
      setLoadingDecisionMakers(newLoadingSet);
    }
  };

  const sendEmail = async (decisionMaker: DecisionMaker, companyName: string) => {
    if (!decisionMaker.email) {
      alert('No email address available for this decision maker');
      return;
    }
    
    const emailKey = `${decisionMaker.email}-${companyName}`;
    const newSendingSet = new Set(sendingEmails);
    newSendingSet.add(emailKey);
    setSendingEmails(newSendingSet);
    
    try {
      console.log(`📧 Sending email to ${decisionMaker.name} at ${decisionMaker.email}`);
      
      await sendPersonalizedEmail({
        recipient_email: decisionMaker.email,
        recipient_name: decisionMaker.name,
        recipient_title: decisionMaker.title,
        company_name: companyName,
        linkedin_profile_url: decisionMaker.linkedin_profile_url
      });
      
      alert(`✅ Personalized email sent to ${decisionMaker.name} at ${decisionMaker.email}!`);
      console.log(`✅ Email sent successfully to ${decisionMaker.email}`);
    } catch (err) {
      console.error(`❌ Error sending email to ${decisionMaker.email}:`, err);
      alert(`❌ Failed to send email to ${decisionMaker.name}: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      const newSendingSet = new Set(sendingEmails);
      newSendingSet.delete(emailKey);
      setSendingEmails(newSendingSet);
    }
  };

  return (
    <div className="container">
      {/* Header */}
      <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2.5rem', fontWeight: 'bold', color: '#1f2937', marginBottom: '1rem' }}>
          🎯 POC Outreach Workflow
        </h1>
        <p style={{ fontSize: '1.1rem', color: '#6b7280' }}>
          Discover and score companies using Crust Data intelligence
        </p>
      </div>

      {/* ICP Form */}
      <div className="form-container">
        <h2 style={{ fontSize: '1.5rem', fontWeight: '600', marginBottom: '1.5rem', color: '#1f2937' }}>
          🎯 Define Your ICP (Ideal Customer Profile)
        </h2>
        
        <form onSubmit={handleSubmit}>
          {/* Industries */}
          <div className="form-group">
            <label className="form-label">Target Industries</label>
            <div className="checkbox-grid">
              {industries.map(industry => (
                <label key={industry} className="checkbox-item">
                  <input
                    type="checkbox"
                    checked={icp.industries.includes(industry)}
                    onChange={(e) => handleIndustryChange(industry, e.target.checked)}
                    style={{ marginRight: '0.5rem' }}
                  />
                  {industry}
                </label>
              ))}
            </div>
            <div style={{ fontSize: '0.875rem', color: '#6b7280', marginTop: '0.5rem' }}>
              Selected: {icp.industries.length} industries
            </div>
          </div>

          {/* Revenue Range */}
          <div className="form-group">
            <label className="form-label">Annual Revenue Range</label>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div>
                <label style={{ fontSize: '0.875rem', color: '#6b7280' }}>Minimum Revenue</label>
                <input
                  type="number"
                  className="form-input"
                  value={icp.revenue_min}
                  onChange={(e) => setIcp(prev => ({ ...prev, revenue_min: Number(e.target.value) }))}
                />
                <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>
                  {formatCurrency(icp.revenue_min)}
                </div>
              </div>
              <div>
                <label style={{ fontSize: '0.875rem', color: '#6b7280' }}>Maximum Revenue</label>
                <input
                  type="number"
                  className="form-input"
                  value={icp.revenue_max}
                  onChange={(e) => setIcp(prev => ({ ...prev, revenue_max: Number(e.target.value) }))}
                />
                <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>
                  {formatCurrency(icp.revenue_max)}
                </div>
              </div>
            </div>
          </div>

          {/* Headcount Range */}
          <div className="form-group">
            <label className="form-label">Employee Count Range</label>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div>
                <label style={{ fontSize: '0.875rem', color: '#6b7280' }}>Minimum Employees</label>
                <input
                  type="number"
                  className="form-input"
                  value={icp.headcount_min}
                  onChange={(e) => setIcp(prev => ({ ...prev, headcount_min: Number(e.target.value) }))}
                />
              </div>
              <div>
                <label style={{ fontSize: '0.875rem', color: '#6b7280' }}>Maximum Employees</label>
                <input
                  type="number"
                  className="form-input"
                  value={icp.headcount_max}
                  onChange={(e) => setIcp(prev => ({ ...prev, headcount_max: Number(e.target.value) }))}
                />
              </div>
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            className="btn-primary"
            disabled={loading || icp.industries.length === 0}
            style={{ width: '100%' }}
          >
            {loading ? (
              <span>
                <span className="loading-spinner" style={{ marginRight: '0.5rem' }}></span>
                Discovering Companies...
              </span>
            ) : (
              '🔍 Find Companies'
            )}
          </button>
        </form>
      </div>

      {/* Error Message */}
      {error && (
        <div style={{
          backgroundColor: '#fef2f2',
          border: '1px solid #fecaca',
          borderRadius: '8px',
          padding: '1rem',
          marginBottom: '1rem'
        }}>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <div style={{ color: '#ef4444', marginRight: '0.5rem' }}>⚠️</div>
            <div>
              <h3 style={{ color: '#991b1b', fontWeight: '600', margin: 0 }}>Search Error</h3>
              <p style={{ color: '#dc2626', fontSize: '0.875rem', margin: '0.25rem 0 0 0' }}>{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Results */}
      {loading && (
        <div className="results-container" style={{ padding: '2rem', textAlign: 'center' }}>
          <div className="loading-spinner" style={{ marginBottom: '1rem' }}></div>
          <h3 style={{ color: '#1f2937', marginBottom: '0.5rem' }}>Discovering Companies</h3>
          <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>
            Searching Crust Data for companies matching your ICP...
          </p>
        </div>
      )}

      {searchResponse && !loading && (
        <div className="results-container">
          {/* Results Header */}
          <div style={{
            padding: '1.5rem',
            backgroundColor: '#f9fafb',
            borderBottom: '1px solid #e5e7eb'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <h2 style={{ fontSize: '1.25rem', fontWeight: '600', color: '#1f2937', margin: 0 }}>
                  Found {searchResponse.total_found} Companies
                </h2>
                <p style={{ fontSize: '0.875rem', color: '#6b7280', margin: '0.25rem 0 0 0' }}>
                  Search completed in {searchResponse.search_time_ms}ms
                </p>
              </div>
            </div>
          </div>

          {/* Company List */}
          {searchResponse.companies.length > 0 ? (
            searchResponse.companies.map((company, index) => (
              <div key={index} className="company-card">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                  {/* Company Info */}
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                      <h3 style={{ fontSize: '1.1rem', fontWeight: '600', color: '#1f2937', margin: 0 }}>
                        {company.name || 'Unknown Company'}
                        {company.domain && (
                          <a 
                            href={`https://${company.domain}`} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            style={{ marginLeft: '0.5rem', color: '#3b82f6', fontSize: '0.875rem', textDecoration: 'none' }}
                          >
                            🔗 {company.domain}
                          </a>
                        )}
                      </h3>
                      
                      {/* Drill-down Button */}
                      <button
                        onClick={() => toggleCompanyExpansion(company.domain, company.name)}
                        style={{
                          backgroundColor: expandedCompanies.has(company.domain) ? '#dc2626' : '#3b82f6',
                          color: 'white',
                          border: 'none',
                          borderRadius: '6px',
                          padding: '0.5rem 1rem',
                          fontSize: '0.875rem',
                          fontWeight: '500',
                          cursor: 'pointer',
                          transition: 'background-color 0.2s',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.5rem'
                        }}
                        disabled={loadingDecisionMakers.has(company.domain)}
                      >
                        {loadingDecisionMakers.has(company.domain) ? (
                          <>
                            <div className="loading-spinner" style={{ width: '12px', height: '12px' }}></div>
                            Loading...
                          </>
                        ) : expandedCompanies.has(company.domain) ? (
                          <>
                            ▼ Hide Decision Makers
                          </>
                        ) : (
                          <>
                            👥 View Decision Makers
                          </>
                        )}
                      </button>
                    </div>
                    
                    <div style={{ 
                      display: 'grid', 
                      gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', 
                      gap: '1rem',
                      marginBottom: '0.75rem'
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center' }}>
                        <span style={{ fontSize: '1.5rem', marginRight: '0.5rem' }}>👥</span>
                        <div>
                          <div style={{ fontWeight: '500', color: '#1f2937' }}>
                            {company.headcount > 0 ? company.headcount.toLocaleString() : 'N/A'} employees
                          </div>
                        </div>
                      </div>
                      
                      <div style={{ display: 'flex', alignItems: 'center' }}>
                        <span style={{ fontSize: '1.5rem', marginRight: '0.5rem' }}>💰</span>
                        <div>
                          <div style={{ fontWeight: '500', color: '#1f2937' }}>
                            {formatCurrency(company.revenue)}
                          </div>
                        </div>
                      </div>
                      
                      <div style={{ display: 'flex', alignItems: 'center' }}>
                        <span style={{ fontSize: '1.5rem', marginRight: '0.5rem' }}>📍</span>
                        <div>
                          <div style={{ fontWeight: '500', color: '#1f2937' }}>
                            {company.headquarters || 'N/A'}
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    {company.industries.length > 0 && (
                      <div>
                        {company.industries.slice(0, 3).map((industry, idx) => (
                          <span
                            key={idx}
                            style={{
                              display: 'inline-block',
                              backgroundColor: '#dbeafe',
                              color: '#1e40af',
                              padding: '0.25rem 0.5rem',
                              borderRadius: '1rem',
                              fontSize: '0.75rem',
                              marginRight: '0.5rem',
                              marginBottom: '0.25rem'
                            }}
                          >
                            {industry}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  
                  {/* Score */}
                  <div style={{ marginLeft: '1rem', textAlign: 'center' }}>
                    <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#1f2937' }}>
                      {Math.round(company.score * 100)}%
                    </div>
                    <div style={{ fontSize: '0.75rem', color: '#6b7280', marginBottom: '0.5rem' }}>
                      ICP Match
                    </div>
                    
                    {/* Score Bar */}
                    <div className="score-bar">
                      <div 
                        className={`score-fill ${
                          company.score >= 0.8 ? 'score-excellent' : 
                          company.score >= 0.6 ? 'score-good' : 
                          company.score >= 0.4 ? 'score-fair' : 'score-poor'
                        }`}
                        style={{ width: `${company.score * 100}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
                
                {/* Decision Makers Section */}
                {expandedCompanies.has(company.domain) && (
                  <div style={{
                    marginTop: '1.5rem',
                    paddingTop: '1.5rem',
                    borderTop: '1px solid #e5e7eb'
                  }}>
                    <h4 style={{ 
                      fontSize: '1rem', 
                      fontWeight: '600', 
                      color: '#1f2937', 
                      marginBottom: '1rem',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem'
                    }}>
                      👥 Decision Makers
                      {companyDecisionMakers[company.domain] && (
                        <span style={{ 
                          fontSize: '0.75rem', 
                          color: '#6b7280', 
                          fontWeight: '400' 
                        }}>
                          ({companyDecisionMakers[company.domain].total_found} found)
                        </span>
                      )}
                    </h4>
                    
                    {loadingDecisionMakers.has(company.domain) ? (
                      <div style={{ textAlign: 'center', padding: '2rem' }}>
                        <div className="loading-spinner" style={{ marginBottom: '0.5rem' }}></div>
                        <div style={{ color: '#6b7280', fontSize: '0.875rem' }}>
                          Loading decision makers...
                        </div>
                      </div>
                    ) : companyDecisionMakers[company.domain]?.decision_makers.length > 0 ? (
                      <div style={{
                        display: 'grid',
                        gap: '1rem',
                        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))'
                      }}>
                        {companyDecisionMakers[company.domain].decision_makers.map((dm, dmIndex) => (
                          <div key={dmIndex} style={{
                            border: '1px solid #e5e7eb',
                            borderRadius: '8px',
                            padding: '1rem',
                            backgroundColor: '#f9fafb'
                          }}>
                            <div style={{ display: 'flex', alignItems: 'start', gap: '1rem' }}>
                              {/* Profile Picture */}
                              <div style={{
                                width: '48px',
                                height: '48px',
                                borderRadius: '24px',
                                backgroundColor: '#ddd',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                fontSize: '1.5rem',
                                flexShrink: 0
                              }}>
                                {dm.profile_picture_url ? (
                                  <img 
                                    src={dm.profile_picture_url} 
                                    alt={dm.name}
                                    style={{ width: '48px', height: '48px', borderRadius: '24px' }}
                                    onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }}
                                  />
                                ) : '👤'}
                              </div>
                              
                              {/* Contact Info */}
                              <div style={{ flex: 1 }}>
                                <h5 style={{ 
                                  fontSize: '1rem', 
                                  fontWeight: '600', 
                                  color: '#1f2937', 
                                  margin: '0 0 0.25rem 0' 
                                }}>
                                  {dm.name}
                                </h5>
                                <div style={{ 
                                  fontSize: '0.875rem', 
                                  color: '#6b7280', 
                                  marginBottom: '0.5rem' 
                                }}>
                                  {dm.title}
                                </div>
                                
                                {dm.location && (
                                  <div style={{ 
                                    fontSize: '0.75rem', 
                                    color: '#6b7280', 
                                    marginBottom: '0.5rem' 
                                  }}>
                                    📍 {dm.location}
                                  </div>
                                )}
                                
                                {dm.email && (
                                  <div style={{ 
                                    fontSize: '0.75rem', 
                                    color: '#059669', 
                                    marginBottom: '0.75rem',
                                    wordBreak: 'break-word'
                                  }}>
                                    ✉️ {dm.email}
                                  </div>
                                )}
                                
                                <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                                  {dm.linkedin_profile_url && (
                                    <a
                                      href={dm.linkedin_profile_url}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                      style={{
                                        color: '#0a66c2',
                                        fontSize: '0.75rem',
                                        textDecoration: 'none',
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '0.25rem'
                                      }}
                                    >
                                      💼 LinkedIn
                                    </a>
                                  )}
                                  
                                  {dm.email && (
                                    <button
                                      onClick={() => sendEmail(dm, company.name)}
                                      disabled={sendingEmails.has(`${dm.email}-${company.name}`)}
                                      style={{
                                        backgroundColor: '#059669',
                                        color: 'white',
                                        border: 'none',
                                        borderRadius: '4px',
                                        padding: '0.375rem 0.75rem',
                                        fontSize: '0.75rem',
                                        fontWeight: '500',
                                        cursor: dm.email ? 'pointer' : 'not-allowed',
                                        opacity: sendingEmails.has(`${dm.email}-${company.name}`) ? 0.6 : 1,
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '0.25rem',
                                        marginLeft: 'auto'
                                      }}
                                    >
                                      {sendingEmails.has(`${dm.email}-${company.name}`) ? (
                                        <>
                                          <div className="loading-spinner" style={{ width: '10px', height: '10px' }}></div>
                                          Sending...
                                        </>
                                      ) : (
                                        <>
                                          📧 Send Email
                                        </>
                                      )}
                                    </button>
                                  )}
                                </div>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div style={{ 
                        textAlign: 'center', 
                        padding: '2rem',
                        color: '#6b7280',
                        fontSize: '0.875rem'
                      }}>
                        <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>🔍</div>
                        No decision makers found for this company.
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))
          ) : (
            <div style={{ padding: '2rem', textAlign: 'center' }}>
              <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🔍</div>
              <h3 style={{ color: '#1f2937', marginBottom: '0.5rem' }}>No Companies Found</h3>
              <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>
                Try adjusting your ICP criteria to find more matches.
              </p>
            </div>
          )}
        </div>
      )}

      {/* Footer */}
      <div style={{ 
        marginTop: '3rem', 
        textAlign: 'center', 
        fontSize: '0.875rem', 
        color: '#6b7280',
        borderTop: '1px solid #e5e7eb',
        paddingTop: '1.5rem'
      }}>
        POC Outreach Workflow • Powered by Crust Data API & FastAPI
      </div>
    </div>
  );
}

export default SimpleApp;