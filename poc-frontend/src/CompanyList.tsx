/**
 * Company List Component - Display search results with scoring
 */

import React from 'react';
import { SearchResponse } from './api';

interface Props {
  searchResponse: SearchResponse | null;
  loading: boolean;
}

const CompanyList: React.FC<Props> = ({ searchResponse, loading }) => {
  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-8">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-4"></div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Discovering Companies
          </h3>
          <p className="text-sm text-gray-500">
            Searching Crust Data for companies matching your ICP...
          </p>
        </div>
      </div>
    );
  }

  if (!searchResponse) {
    return (
      <div className="bg-white rounded-lg shadow-md p-8 text-center">
        <div className="text-6xl mb-4">🎯</div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          Ready to Find Your Ideal Customers
        </h3>
        <p className="text-sm text-gray-500">
          Define your ICP criteria above and click "Find Companies" to discover potential customers.
        </p>
      </div>
    );
  }

  const { companies, total_found, search_time_ms, icp } = searchResponse;

  if (companies.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-8 text-center">
        <div className="text-6xl mb-4">🔍</div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          No Companies Found
        </h3>
        <p className="text-sm text-gray-500 mb-4">
          No companies match your current ICP criteria. Try adjusting your filters:
        </p>
        <ul className="text-sm text-gray-600 space-y-1">
          <li>• Expand your revenue range</li>
          <li>• Increase headcount limits</li>
          <li>• Add more industries</li>
        </ul>
      </div>
    );
  }

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

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'bg-green-500';
    if (score >= 0.6) return 'bg-blue-500';
    if (score >= 0.4) return 'bg-yellow-500';
    return 'bg-gray-500';
  };

  const getScoreLabel = (score: number) => {
    if (score >= 0.8) return 'Excellent Match';
    if (score >= 0.6) return 'Good Match';
    if (score >= 0.4) return 'Fair Match';
    return 'Potential';
  };

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 bg-gray-50 border-b">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">
              Found {total_found} Companies
            </h2>
            <p className="text-sm text-gray-500">
              Search completed in {search_time_ms}ms • Showing top {companies.length} results
            </p>
          </div>
          <div className="text-right">
            <div className="text-sm text-gray-500">Target Industries:</div>
            <div className="text-sm font-medium text-blue-600">
              {icp.industries.join(', ')}
            </div>
          </div>
        </div>
      </div>
      
      {/* Company Cards - Mobile Friendly */}
      <div className="divide-y divide-gray-200">
        {companies.map((company, index) => (
          <div key={index} className="p-6 hover:bg-gray-50 transition-colors">
            <div className="flex items-start justify-between">
              {/* Company Info */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center mb-2">
                  <h3 className="text-lg font-semibold text-gray-900 truncate">
                    {company.name || 'Unknown Company'}
                  </h3>
                  {company.domain && (
                    <a 
                      href={`https://${company.domain}`} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="ml-2 text-blue-500 hover:text-blue-700 text-sm"
                    >
                      🔗 {company.domain}
                    </a>
                  )}
                </div>
                
                {/* Company Stats */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-3">
                  <div className="flex items-center">
                    <span className="text-2xl mr-2">👥</span>
                    <div>
                      <div className="text-sm font-medium text-gray-900">
                        {company.headcount > 0 ? company.headcount.toLocaleString() : 'N/A'} employees
                      </div>
                      <div className="text-xs text-gray-500">Team size</div>
                    </div>
                  </div>
                  
                  <div className="flex items-center">
                    <span className="text-2xl mr-2">💰</span>
                    <div>
                      <div className="text-sm font-medium text-gray-900">
                        {formatCurrency(company.revenue)}
                      </div>
                      <div className="text-xs text-gray-500">Annual revenue</div>
                    </div>
                  </div>
                  
                  <div className="flex items-center">
                    <span className="text-2xl mr-2">📍</span>
                    <div>
                      <div className="text-sm font-medium text-gray-900 truncate">
                        {company.headquarters || 'N/A'}
                      </div>
                      <div className="text-xs text-gray-500">Headquarters</div>
                    </div>
                  </div>
                </div>
                
                {/* Industries */}
                {company.industries.length > 0 && (
                  <div className="mb-3">
                    <div className="flex flex-wrap gap-1">
                      {company.industries.slice(0, 3).map((industry, idx) => (
                        <span
                          key={idx}
                          className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-800"
                        >
                          {industry}
                        </span>
                      ))}
                      {company.industries.length > 3 && (
                        <span className="text-xs text-gray-500">
                          +{company.industries.length - 3} more
                        </span>
                      )}
                    </div>
                  </div>
                )}
                
                {/* Founded Year */}
                {company.founded_year && (
                  <div className="text-xs text-gray-500">
                    Founded: {company.founded_year}
                  </div>
                )}
              </div>
              
              {/* Score */}
              <div className="ml-4 flex flex-col items-end">
                <div className="text-center mb-2">
                  <div className="text-2xl font-bold text-gray-900">
                    {Math.round(company.score * 100)}%
                  </div>
                  <div className="text-xs text-gray-500">ICP Match</div>
                </div>
                
                {/* Score Bar */}
                <div className="w-20 bg-gray-200 rounded-full h-2 mb-1">
                  <div 
                    className={`h-2 rounded-full ${getScoreColor(company.score)}`}
                    style={{ width: `${company.score * 100}%` }}
                  ></div>
                </div>
                
                <div className={`text-xs font-medium ${
                  company.score >= 0.6 ? 'text-green-600' : 'text-gray-600'
                }`}>
                  {getScoreLabel(company.score)}
                </div>
                
                {/* Action Button */}
                <button className="mt-3 px-4 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 transition-colors">
                  View Details
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      {/* Footer */}
      {total_found > companies.length && (
        <div className="px-6 py-4 bg-gray-50 border-t text-center">
          <p className="text-sm text-gray-500">
            Showing {companies.length} of {total_found} companies. 
            <span className="ml-1 text-blue-600 font-medium cursor-pointer hover:text-blue-700">
              Load more results
            </span>
          </p>
        </div>
      )}
    </div>
  );
};

export default CompanyList;