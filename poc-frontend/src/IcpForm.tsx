/**
 * ICP Form Component - Define Ideal Customer Profile criteria
 */

import React, { useState, useEffect } from 'react';
import { ICP, getAvailableIndustries } from './api';

interface Props {
  onSearch: (icp: ICP) => void;
  loading: boolean;
}

const IcpForm: React.FC<Props> = ({ onSearch, loading }) => {
  const [icp, setIcp] = useState<ICP>({
    industries: ['Technology'],
    revenue_min: 10000000,      // $10M
    revenue_max: 1000000000,    // $1B
    headcount_min: 100,
    headcount_max: 5000
  });

  const [availableIndustries, setAvailableIndustries] = useState<string[]>([]);
  const [loadingIndustries, setLoadingIndustries] = useState(true);

  // Load available industries on component mount
  useEffect(() => {
    const loadIndustries = async () => {
      try {
        const industries = await getAvailableIndustries();
        setAvailableIndustries(industries);
      } catch (error) {
        console.error('Failed to load industries:', error);
        // Fallback industries
        setAvailableIndustries([
          'Technology', 'Software', 'Fintech', 'E-commerce', 'SaaS',
          'Healthcare', 'Manufacturing', 'Retail', 'Consulting'
        ]);
      } finally {
        setLoadingIndustries(false);
      }
    };

    loadIndustries();
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validation
    if (icp.industries.length === 0) {
      alert('Please select at least one industry');
      return;
    }
    
    if (icp.revenue_min >= icp.revenue_max) {
      alert('Maximum revenue must be greater than minimum revenue');
      return;
    }
    
    if (icp.headcount_min >= icp.headcount_max) {
      alert('Maximum headcount must be greater than minimum headcount');
      return;
    }

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

  const formatCurrency = (value: number) => {
    if (value >= 1000000000) {
      return `$${(value / 1000000000).toFixed(1)}B`;
    } else if (value >= 1000000) {
      return `$${(value / 1000000).toFixed(0)}M`;
    } else {
      return `$${value.toLocaleString()}`;
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow-md mb-8">
      <h2 className="text-2xl font-bold mb-6 text-gray-900">
        🎯 Define Your ICP (Ideal Customer Profile)
      </h2>
      
      {/* Industries Selection */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Target Industries
        </label>
        {loadingIndustries ? (
          <div className="text-sm text-gray-500">Loading industries...</div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {availableIndustries.map(industry => (
              <label key={industry} className="flex items-center p-2 border rounded-md hover:bg-gray-50">
                <input
                  type="checkbox"
                  checked={icp.industries.includes(industry)}
                  onChange={(e) => handleIndustryChange(industry, e.target.checked)}
                  className="mr-3 h-4 w-4 text-blue-600"
                />
                <span className="text-sm">{industry}</span>
              </label>
            ))}
          </div>
        )}
        <div className="text-xs text-gray-500 mt-2">
          Selected: {icp.industries.length} industries
        </div>
      </div>

      {/* Revenue Range */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Annual Revenue Range
        </label>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-xs text-gray-500 mb-1">Minimum Revenue</label>
            <input
              type="number"
              min="0"
              value={icp.revenue_min}
              onChange={(e) => setIcp(prev => ({ ...prev, revenue_min: Number(e.target.value) }))}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="1000000"
            />
            <div className="text-xs text-gray-500 mt-1">{formatCurrency(icp.revenue_min)}</div>
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">Maximum Revenue</label>
            <input
              type="number"
              min="0"
              value={icp.revenue_max}
              onChange={(e) => setIcp(prev => ({ ...prev, revenue_max: Number(e.target.value) }))}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="100000000"
            />
            <div className="text-xs text-gray-500 mt-1">{formatCurrency(icp.revenue_max)}</div>
          </div>
        </div>
      </div>

      {/* Headcount Range */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Employee Count Range
        </label>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-xs text-gray-500 mb-1">Minimum Employees</label>
            <input
              type="number"
              min="1"
              value={icp.headcount_min}
              onChange={(e) => setIcp(prev => ({ ...prev, headcount_min: Number(e.target.value) }))}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="50"
            />
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">Maximum Employees</label>
            <input
              type="number"
              min="1"
              value={icp.headcount_max}
              onChange={(e) => setIcp(prev => ({ ...prev, headcount_max: Number(e.target.value) }))}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="1000"
            />
          </div>
        </div>
      </div>

      {/* Search Button */}
      <button
        type="submit"
        disabled={loading || icp.industries.length === 0}
        className="w-full bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
      >
        {loading ? (
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
            Discovering Companies...
          </div>
        ) : (
          '🔍 Find Companies'
        )}
      </button>
      
      {/* Quick ICP Templates */}
      <div className="mt-4 pt-4 border-t">
        <div className="text-sm text-gray-600 mb-2">Quick Templates:</div>
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => setIcp({
              industries: ['Technology', 'Software'],
              revenue_min: 10000000,
              revenue_max: 500000000,
              headcount_min: 100,
              headcount_max: 2000
            })}
            className="px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded-full hover:bg-gray-200"
          >
            Tech Scale-ups
          </button>
          <button
            type="button"
            onClick={() => setIcp({
              industries: ['Fintech', 'SaaS'],
              revenue_min: 5000000,
              revenue_max: 100000000,
              headcount_min: 50,
              headcount_max: 1000
            })}
            className="px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded-full hover:bg-gray-200"
          >
            Fintech Startups
          </button>
          <button
            type="button"
            onClick={() => setIcp({
              industries: ['E-commerce', 'Retail'],
              revenue_min: 20000000,
              revenue_max: 1000000000,
              headcount_min: 200,
              headcount_max: 5000
            })}
            className="px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded-full hover:bg-gray-200"
          >
            E-commerce Leaders
          </button>
        </div>
      </div>
    </form>
  );
};

export default IcpForm;