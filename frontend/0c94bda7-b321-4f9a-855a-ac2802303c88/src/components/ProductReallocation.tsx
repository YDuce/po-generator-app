import React from 'react';
import { ArrowRightIcon, RefreshCwIcon, TrendingUpIcon, AlertTriangleIcon } from 'lucide-react';
export function ProductReallocation() {
  const reallocationSuggestions = [{
    id: 1,
    product: 'Wireless Headphones',
    currentPlatform: 'eBay',
    suggestedPlatform: 'Amazon',
    reason: 'Higher profit margin',
    potentialIncrease: '+28%',
    priority: 'High',
    inventory: 45
  }, {
    id: 2,
    product: 'Phone Case',
    currentPlatform: 'Shopify',
    suggestedPlatform: 'Amazon',
    reason: 'Better conversion rate',
    potentialIncrease: '+15%',
    priority: 'Medium',
    inventory: 89
  }, {
    id: 3,
    product: 'Laptop Stand',
    currentPlatform: 'Amazon',
    suggestedPlatform: 'Etsy',
    reason: 'Lower competition',
    potentialIncrease: '+18%',
    priority: 'Medium',
    inventory: 34
  }, {
    id: 4,
    product: 'USB Cable',
    currentPlatform: 'eBay',
    suggestedPlatform: 'Shopify',
    reason: 'Higher average order value',
    potentialIncrease: '+12%',
    priority: 'Low',
    inventory: 156
  }];
  return <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">
          Product Reallocation
        </h1>
        <button className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center space-x-2 hover:bg-blue-700 transition-colors">
          <RefreshCwIcon className="w-4 h-4" />
          <span>Refresh Analysis</span>
        </button>
      </div>
      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center space-x-3">
            <div className="p-3 rounded-full bg-blue-100">
              <TrendingUpIcon className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600">
                Potential Revenue Increase
              </p>
              <p className="text-2xl font-bold text-gray-900">+18.5%</p>
            </div>
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center space-x-3">
            <div className="p-3 rounded-full bg-yellow-100">
              <RefreshCwIcon className="w-6 h-6 text-yellow-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600">
                Suggested Moves
              </p>
              <p className="text-2xl font-bold text-gray-900">
                {reallocationSuggestions.length}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center space-x-3">
            <div className="p-3 rounded-full bg-red-100">
              <AlertTriangleIcon className="w-6 h-6 text-red-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600">High Priority</p>
              <p className="text-2xl font-bold text-gray-900">
                {reallocationSuggestions.filter(s => s.priority === 'High').length}
              </p>
            </div>
          </div>
        </div>
      </div>
      {/* Reallocation Suggestions */}
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="p-6 border-b">
          <h2 className="text-xl font-semibold text-gray-900">
            Reallocation Suggestions
          </h2>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            {reallocationSuggestions.map(suggestion => <div key={suggestion.id} className="border rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-1">
                    <h3 className="font-medium text-gray-900">
                      {suggestion.product}
                    </h3>
                    <div className="flex items-center text-sm text-gray-500">
                      <span>{suggestion.currentPlatform}</span>
                      <ArrowRightIcon className="w-4 h-4 mx-2" />
                      <span className="font-medium text-blue-600">
                        {suggestion.suggestedPlatform}
                      </span>
                    </div>
                  </div>
                  <span className={`px-2 py-1 text-xs rounded-full ${suggestion.priority === 'High' ? 'bg-red-100 text-red-800' : suggestion.priority === 'Medium' ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'}`}>
                    {suggestion.priority} Priority
                  </span>
                </div>
                <div className="mt-3 grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Reason:</span>
                    <span className="ml-2 text-gray-900">
                      {suggestion.reason}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-600">Potential Increase:</span>
                    <span className="ml-2 text-green-600 font-medium">
                      {suggestion.potentialIncrease}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-600">Current Inventory:</span>
                    <span className="ml-2 text-gray-900">
                      {suggestion.inventory} units
                    </span>
                  </div>
                </div>
                <div className="mt-3">
                  <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">
                    Review & Apply
                  </button>
                </div>
              </div>)}
          </div>
        </div>
      </div>
    </div>;
}