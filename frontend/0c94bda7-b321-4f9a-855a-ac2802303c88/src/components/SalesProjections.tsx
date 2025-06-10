import React from 'react';
import { TrendingUpIcon, TrendingDownIcon, BarChart3Icon } from 'lucide-react';
export function SalesProjections() {
  const projections = [{
    product: 'Wireless Headphones',
    currentMonth: 145,
    projected: 180,
    growth: '+24%',
    trend: 'up'
  }, {
    product: 'Bluetooth Speaker',
    currentMonth: 89,
    projected: 95,
    growth: '+7%',
    trend: 'up'
  }, {
    product: 'Phone Case',
    currentMonth: 234,
    projected: 210,
    growth: '-10%',
    trend: 'down'
  }, {
    product: 'Laptop Stand',
    currentMonth: 67,
    projected: 85,
    growth: '+27%',
    trend: 'up'
  }, {
    product: 'USB Cable',
    currentMonth: 456,
    projected: 520,
    growth: '+14%',
    trend: 'up'
  }];
  const platformProjections = [{
    platform: 'Amazon',
    current: 28450,
    projected: 32100,
    growth: '+13%'
  }, {
    platform: 'eBay',
    current: 18230,
    projected: 19500,
    growth: '+7%'
  }, {
    platform: 'Shopify',
    current: 12840,
    projected: 15200,
    growth: '+18%'
  }, {
    platform: 'Etsy',
    current: 6320,
    projected: 6800,
    growth: '+8%'
  }];
  return <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Sales Projections</h1>
        <div className="flex items-center space-x-2 text-sm text-gray-500">
          <BarChart3Icon className="w-4 h-4" />
          <span>Next 30 days forecast</span>
        </div>
      </div>
      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">
                Projected Revenue
              </p>
              <p className="text-2xl font-bold text-gray-900 mt-1">$73,600</p>
              <p className="text-sm text-green-600 mt-1">
                +12% from current month
              </p>
            </div>
            <div className="p-3 rounded-full bg-green-100">
              <TrendingUpIcon className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Units to Sell</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">1,090</p>
              <p className="text-sm text-green-600 mt-1">
                +8% from current month
              </p>
            </div>
            <div className="p-3 rounded-full bg-blue-100">
              <BarChart3Icon className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">
                Avg. Order Value
              </p>
              <p className="text-2xl font-bold text-gray-900 mt-1">$67.52</p>
              <p className="text-sm text-green-600 mt-1">
                +3% from current month
              </p>
            </div>
            <div className="p-3 rounded-full bg-purple-100">
              <TrendingUpIcon className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </div>
      </div>
      {/* Product Projections */}
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="p-6 border-b">
          <h2 className="text-xl font-semibold text-gray-900">
            Product Sales Projections
          </h2>
        </div>
        <div className="p-6">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="text-left text-sm font-medium text-gray-500 border-b">
                  <th className="pb-3">Product</th>
                  <th className="pb-3">Current Month</th>
                  <th className="pb-3">Projected</th>
                  <th className="pb-3">Growth</th>
                  <th className="pb-3">Trend</th>
                </tr>
              </thead>
              <tbody>
                {projections.map(item => <tr key={item.product} className="border-b last:border-b-0">
                    <td className="py-3 font-medium text-gray-900">
                      {item.product}
                    </td>
                    <td className="py-3 text-gray-600">
                      {item.currentMonth} units
                    </td>
                    <td className="py-3 font-medium text-gray-900">
                      {item.projected} units
                    </td>
                    <td className="py-3">
                      <span className={`font-medium ${item.trend === 'up' ? 'text-green-600' : 'text-red-600'}`}>
                        {item.growth}
                      </span>
                    </td>
                    <td className="py-3">
                      {item.trend === 'up' ? <TrendingUpIcon className="w-5 h-5 text-green-600" /> : <TrendingDownIcon className="w-5 h-5 text-red-600" />}
                    </td>
                  </tr>)}
              </tbody>
            </table>
          </div>
        </div>
      </div>
      {/* Platform Projections */}
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="p-6 border-b">
          <h2 className="text-xl font-semibold text-gray-900">
            Platform Revenue Projections
          </h2>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {platformProjections.map(platform => <div key={platform.platform} className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-medium text-gray-900">
                    {platform.platform}
                  </h3>
                  <span className="text-sm text-green-600 font-medium">
                    {platform.growth}
                  </span>
                </div>
                <div className="space-y-1">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Current</span>
                    <span className="font-medium">
                      ${platform.current.toLocaleString()}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Projected</span>
                    <span className="font-medium text-green-600">
                      ${platform.projected.toLocaleString()}
                    </span>
                  </div>
                </div>
              </div>)}
          </div>
        </div>
      </div>
    </div>;
}