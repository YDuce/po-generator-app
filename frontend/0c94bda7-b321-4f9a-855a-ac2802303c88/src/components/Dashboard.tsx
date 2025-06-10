import React from 'react';
import { TrendingUpIcon, PackageIcon, DollarSignIcon, AlertTriangleIcon } from 'lucide-react';
export function Dashboard() {
  const stats = [{
    label: 'Total Products',
    value: '1,247',
    change: '+12%',
    icon: PackageIcon,
    color: 'blue'
  }, {
    label: 'Monthly Revenue',
    value: '$48,329',
    change: '+8.2%',
    icon: DollarSignIcon,
    color: 'green'
  }, {
    label: 'Active Platforms',
    value: '5',
    change: '+1',
    icon: TrendingUpIcon,
    color: 'purple'
  }, {
    label: 'Low Stock Alerts',
    value: '23',
    change: '-5',
    icon: AlertTriangleIcon,
    color: 'red'
  }];
  const platforms = [{
    name: 'Amazon',
    revenue: '$18,450',
    products: 324,
    status: 'Active'
  }, {
    name: 'eBay',
    revenue: '$12,230',
    products: 189,
    status: 'Active'
  }, {
    name: 'Shopify',
    revenue: '$9,840',
    products: 267,
    status: 'Active'
  }, {
    name: 'Etsy',
    revenue: '$4,320',
    products: 156,
    status: 'Active'
  }, {
    name: 'Walmart',
    revenue: '$3,489',
    products: 311,
    status: 'Pending'
  }];
  return <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <div className="text-sm text-gray-500">Last updated: 2 minutes ago</div>
      </div>
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map(stat => {
        const Icon = stat.icon;
        return <div key={stat.label} className="bg-white p-6 rounded-lg shadow-sm border">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">
                    {stat.label}
                  </p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">
                    {stat.value}
                  </p>
                  <p className={`text-sm mt-1 ${stat.change.startsWith('+') ? 'text-green-600' : 'text-red-600'}`}>
                    {stat.change} from last month
                  </p>
                </div>
                <div className={`p-3 rounded-full bg-${stat.color}-100`}>
                  <Icon className={`w-6 h-6 text-${stat.color}-600`} />
                </div>
              </div>
            </div>;
      })}
      </div>
      {/* Platform Performance */}
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="p-6 border-b">
          <h2 className="text-xl font-semibold text-gray-900">
            Platform Performance
          </h2>
        </div>
        <div className="p-6">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="text-left text-sm font-medium text-gray-500 border-b">
                  <th className="pb-3">Platform</th>
                  <th className="pb-3">Revenue</th>
                  <th className="pb-3">Products</th>
                  <th className="pb-3">Status</th>
                </tr>
              </thead>
              <tbody className="space-y-2">
                {platforms.map(platform => <tr key={platform.name} className="border-b last:border-b-0">
                    <td className="py-3 font-medium text-gray-900">
                      {platform.name}
                    </td>
                    <td className="py-3 text-gray-600">{platform.revenue}</td>
                    <td className="py-3 text-gray-600">{platform.products}</td>
                    <td className="py-3">
                      <span className={`px-2 py-1 text-xs rounded-full ${platform.status === 'Active' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                        {platform.status}
                      </span>
                    </td>
                  </tr>)}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>;
}