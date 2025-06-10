import React, { useState } from 'react';
import { SearchIcon, FilterIcon, PlusIcon, EditIcon, TrashIcon } from 'lucide-react';
export function InventoryManagement() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedPlatform, setSelectedPlatform] = useState('all');
  const products = [{
    id: 1,
    name: 'Wireless Headphones',
    sku: 'WH-001',
    amazon: 45,
    ebay: 23,
    shopify: 12,
    totalStock: 80,
    price: '$89.99'
  }, {
    id: 2,
    name: 'Bluetooth Speaker',
    sku: 'BS-002',
    amazon: 67,
    ebay: 34,
    shopify: 28,
    totalStock: 129,
    price: '$59.99'
  }, {
    id: 3,
    name: 'Phone Case',
    sku: 'PC-003',
    amazon: 156,
    ebay: 89,
    shopify: 45,
    totalStock: 290,
    price: '$19.99'
  }, {
    id: 4,
    name: 'Laptop Stand',
    sku: 'LS-004',
    amazon: 23,
    ebay: 12,
    shopify: 8,
    totalStock: 43,
    price: '$39.99'
  }, {
    id: 5,
    name: 'USB Cable',
    sku: 'UC-005',
    amazon: 234,
    ebay: 167,
    shopify: 123,
    totalStock: 524,
    price: '$12.99'
  }];
  const platforms = ['all', 'amazon', 'ebay', 'shopify'];
  const filteredProducts = products.filter(product => product.name.toLowerCase().includes(searchTerm.toLowerCase()) || product.sku.toLowerCase().includes(searchTerm.toLowerCase()));
  return <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">
          Inventory Management
        </h1>
        <button className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center space-x-2 hover:bg-blue-700 transition-colors">
          <PlusIcon className="w-4 h-4" />
          <span>Add Product</span>
        </button>
      </div>
      {/* Search and Filter */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1 relative">
            <SearchIcon className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input type="text" placeholder="Search products or SKU..." value={searchTerm} onChange={e => setSearchTerm(e.target.value)} className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500" />
          </div>
          <div className="flex items-center space-x-2">
            <FilterIcon className="w-5 h-5 text-gray-400" />
            <select value={selectedPlatform} onChange={e => setSelectedPlatform(e.target.value)} className="border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
              {platforms.map(platform => <option key={platform} value={platform}>
                  {platform === 'all' ? 'All Platforms' : platform.charAt(0).toUpperCase() + platform.slice(1)}
                </option>)}
            </select>
          </div>
        </div>
      </div>
      {/* Products Table */}
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="p-6 border-b">
          <h2 className="text-xl font-semibold text-gray-900">
            Products ({filteredProducts.length})
          </h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="text-left text-sm font-medium text-gray-500 border-b">
                <th className="p-4">Product</th>
                <th className="p-4">SKU</th>
                <th className="p-4">Amazon</th>
                <th className="p-4">eBay</th>
                <th className="p-4">Shopify</th>
                <th className="p-4">Total Stock</th>
                <th className="p-4">Price</th>
                <th className="p-4">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredProducts.map(product => <tr key={product.id} className="border-b last:border-b-0 hover:bg-gray-50">
                  <td className="p-4 font-medium text-gray-900">
                    {product.name}
                  </td>
                  <td className="p-4 text-gray-600">{product.sku}</td>
                  <td className="p-4">
                    <span className={`px-2 py-1 text-xs rounded-full ${product.amazon < 20 ? 'bg-red-100 text-red-800' : product.amazon < 50 ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'}`}>
                      {product.amazon}
                    </span>
                  </td>
                  <td className="p-4">
                    <span className={`px-2 py-1 text-xs rounded-full ${product.ebay < 20 ? 'bg-red-100 text-red-800' : product.ebay < 50 ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'}`}>
                      {product.ebay}
                    </span>
                  </td>
                  <td className="p-4">
                    <span className={`px-2 py-1 text-xs rounded-full ${product.shopify < 20 ? 'bg-red-100 text-red-800' : product.shopify < 50 ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'}`}>
                      {product.shopify}
                    </span>
                  </td>
                  <td className="p-4 font-medium">{product.totalStock}</td>
                  <td className="p-4 font-medium text-green-600">
                    {product.price}
                  </td>
                  <td className="p-4">
                    <div className="flex space-x-2">
                      <button className="p-1 text-blue-600 hover:bg-blue-50 rounded">
                        <EditIcon className="w-4 h-4" />
                      </button>
                      <button className="p-1 text-red-600 hover:bg-red-50 rounded">
                        <TrashIcon className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>)}
            </tbody>
          </table>
        </div>
      </div>
    </div>;
}