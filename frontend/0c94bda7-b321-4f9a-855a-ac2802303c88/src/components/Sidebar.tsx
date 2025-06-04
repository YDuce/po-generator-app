import React from 'react';
import { BarChart3Icon, PackageIcon, TrendingUpIcon, CalendarIcon, ArrowRightLeftIcon, HomeIcon } from 'lucide-react';
interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}
export function Sidebar({
  activeTab,
  setActiveTab
}: SidebarProps) {
  const menuItems = [{
    id: 'dashboard',
    label: 'Dashboard',
    icon: HomeIcon
  }, {
    id: 'inventory',
    label: 'Inventory',
    icon: PackageIcon
  }, {
    id: 'projections',
    label: 'Sales Projections',
    icon: TrendingUpIcon
  }, {
    id: 'events',
    label: 'Event Tracker',
    icon: CalendarIcon
  }, {
    id: 'reallocation',
    label: 'Product Reallocation',
    icon: ArrowRightLeftIcon
  }];
  return <div className="w-64 bg-white shadow-lg">
      <div className="p-6 border-b">
        <div className="flex items-center space-x-2">
          <BarChart3Icon className="w-8 h-8 text-blue-600" />
          <h1 className="text-xl font-bold text-gray-900">Seller Hub</h1>
        </div>
      </div>
      <nav className="p-4">
        <ul className="space-y-2">
          {menuItems.map(item => {
          const Icon = item.icon;
          return <li key={item.id}>
                <button onClick={() => setActiveTab(item.id)} className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-left transition-colors ${activeTab === item.id ? 'bg-blue-50 text-blue-700 border-l-4 border-blue-600' : 'text-gray-600 hover:bg-gray-50'}`}>
                  <Icon className="w-5 h-5" />
                  <span className="font-medium">{item.label}</span>
                </button>
              </li>;
        })}
        </ul>
      </nav>
    </div>;
}