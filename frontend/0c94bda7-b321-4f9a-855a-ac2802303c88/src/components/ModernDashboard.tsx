import React from 'react';
import { TrendingUp, AlertTriangle, Calendar, Activity, ExternalLink, ArrowUpRight, ArrowDownRight, Bot, Bell, Package, DollarSign } from 'lucide-react';
interface ModernDashboardProps {
  activeView: string;
  onChannelSelect: (channel: any) => void;
}
export function ModernDashboard({
  activeView,
  onChannelSelect
}: ModernDashboardProps) {
  const channels = [{
    id: 'amazon',
    name: 'Amazon',
    status: 'Connected',
    products: 847,
    revenue: '$34,521',
    change: '+12%',
    trend: 'up',
    syncStatus: 'Up to date',
    lastSync: '2 min ago'
  }, {
    id: 'ebay',
    name: 'eBay',
    status: 'Syncing',
    products: 623,
    revenue: '$18,943',
    change: '+8%',
    trend: 'up',
    syncStatus: 'In progress',
    lastSync: '15 min ago'
  }, {
    id: 'shopify',
    name: 'Shopify',
    status: 'Connected',
    products: 412,
    revenue: '$12,087',
    change: '-3%',
    trend: 'down',
    syncStatus: 'Up to date',
    lastSync: '5 min ago'
  }];
  const kpiCards = [{
    title: 'Total Products',
    value: '1,220',
    subtitle: 'Across 3 platforms',
    icon: Package,
    trend: '+5%'
  }, {
    title: 'Low Stock Items',
    value: '2',
    subtitle: 'Needs attention',
    icon: AlertTriangle,
    trend: '-1',
    alert: true
  }, {
    title: 'Out of Stock',
    value: '1',
    subtitle: 'Requires immediate action',
    icon: AlertTriangle,
    trend: '0',
    critical: true
  }, {
    title: 'Upcoming Events',
    value: '3',
    subtitle: 'In the next 7 days',
    icon: Calendar,
    trend: '+2'
  }];
  const recentActivity = [{
    id: 1,
    message: 'Amazon inventory sync completed',
    time: '2m ago',
    type: 'success'
  }, {
    id: 2,
    message: 'Low stock alert: Eco-Friendly Water Bottle',
    time: '15m ago',
    type: 'warning'
  }, {
    id: 3,
    message: 'eBay listing updated: Bamboo Cutlery Set',
    time: '1h ago',
    type: 'info'
  }, {
    id: 4,
    message: 'Shopify order processed: $89.99',
    time: '2h ago',
    type: 'success'
  }];
  const aiRecommendations = [{
    id: 1,
    title: 'Restock Recommendation',
    message: 'Consider restocking Eco-Friendly Water Bottle - projected to sell out in 3 days',
    priority: 'high',
    action: 'View Details'
  }, {
    id: 2,
    title: 'Price Optimization',
    message: 'Bamboo Cutlery Set could be priced 8% higher based on competitor analysis',
    priority: 'medium',
    action: 'Optimize'
  }, {
    id: 3,
    title: 'Channel Expansion',
    message: 'Solar-Powered Charger performing well on Amazon - consider listing on eBay',
    priority: 'low',
    action: 'Expand'
  }];
  if (activeView !== 'dashboard') {
    return <div className="p-8 bg-background-light dark:bg-background-dark min-h-screen w-full">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-2xl font-semibold mb-6 capitalize">
            {activeView}
          </h1>
          <div className="bg-white dark:bg-border-dark border border-border-light dark:border-border-dark rounded-lg p-8 text-center">
            <Activity className="w-12 h-12 text-accent mx-auto mb-4" />
            <p className="text-gray-500 dark:text-gray-400">
              {activeView.charAt(0).toUpperCase() + activeView.slice(1)} view
              coming soon
            </p>
          </div>
        </div>
      </div>;
  }
  return <div className="p-6 bg-background-light dark:bg-background-dark min-h-screen w-full">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold">Dashboard</h1>
            <p className="text-gray-500 dark:text-gray-400 mt-1">
              Welcome back! Here's an overview of your multi-platform inventory.
            </p>
          </div>
          <div className="flex items-center space-x-3">
            <button className="flex items-center space-x-2 px-4 py-2 text-sm border border-border-light dark:border-border-dark rounded-lg hover:bg-white dark:hover:bg-border-dark transition-colors">
              <Calendar className="w-4 h-4" />
              <span>Last 7 days</span>
            </button>
          </div>
        </div>
        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {kpiCards.map(card => {
          const Icon = card.icon;
          return <div key={card.title} className={`bg-white dark:bg-border-dark border rounded-lg p-4 ${card.critical ? 'border-danger' : card.alert ? 'border-yellow-400' : 'border-border-light dark:border-border-dark'}`}>
                <div className="flex items-center justify-between mb-2">
                  <Icon className={`w-5 h-5 ${card.critical ? 'text-danger' : card.alert ? 'text-yellow-500' : 'text-accent'}`} />
                  <span className={`text-sm font-medium ${card.trend.startsWith('+') ? 'text-success' : card.trend.startsWith('-') ? 'text-danger' : 'text-gray-500'}`}>
                    {card.trend}
                  </span>
                </div>
                <div className="space-y-1">
                  <p className="text-2xl font-bold">{card.value}</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {card.subtitle}
                  </p>
                </div>
              </div>;
        })}
        </div>
        {/* Channels Overview */}
        <div className="bg-white dark:bg-border-dark border border-border-light dark:border-border-dark rounded-lg">
          <div className="p-6 border-b border-border-light dark:border-border-dark">
            <h2 className="text-lg font-semibold">Channels</h2>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {channels.map(channel => <div key={channel.id} className="border border-border-light dark:border-border-dark rounded-lg p-4">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <div className={`w-3 h-3 rounded-full ${channel.status === 'Connected' ? 'bg-success' : 'bg-yellow-500'}`} />
                      <h3 className="font-semibold">{channel.name}</h3>
                    </div>
                    <button onClick={() => onChannelSelect(channel)} className="text-accent hover:text-accent/80 transition-colors">
                      <ExternalLink className="w-4 h-4" />
                    </button>
                  </div>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-500">
                        Products Listed
                      </span>
                      <span className="font-medium">{channel.products}</span>
                    </div>
                    <div className="w-full bg-background-light dark:bg-background-dark rounded-full h-2">
                      <div className="bg-accent h-2 rounded-full" style={{
                    width: `${channel.products / 1000 * 100}%`
                  }} />
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-500">
                        Revenue (30d)
                      </span>
                      <div className="flex items-center space-x-2">
                        <span className="font-semibold">{channel.revenue}</span>
                        <div className={`flex items-center ${channel.trend === 'up' ? 'text-success' : 'text-danger'}`}>
                          {channel.trend === 'up' ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
                          <span className="text-sm">{channel.change}</span>
                        </div>
                      </div>
                    </div>
                    <div className="pt-2 border-t border-border-light dark:border-border-dark">
                      <div className="flex justify-between items-center text-sm">
                        <span className="text-gray-500">Last Sync</span>
                        <span>{channel.lastSync}</span>
                      </div>
                    </div>
                  </div>
                </div>)}
            </div>
          </div>
        </div>
        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Recent Activity */}
          <div className="lg:col-span-2 bg-white dark:bg-border-dark border border-border-light dark:border-border-dark rounded-lg">
            <div className="p-6 border-b border-border-light dark:border-border-dark">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold">Recent Activity</h2>
                <Bell className="w-5 h-5 text-gray-400" />
              </div>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                {recentActivity.map(activity => <div key={activity.id} className="flex items-start space-x-3">
                    <div className={`w-2 h-2 rounded-full mt-2 ${activity.type === 'success' ? 'bg-success' : activity.type === 'warning' ? 'bg-yellow-500' : 'bg-accent'}`} />
                    <div className="flex-1">
                      <p className="text-sm">{activity.message}</p>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        {activity.time}
                      </p>
                    </div>
                  </div>)}
              </div>
            </div>
          </div>
          {/* AI Recommendations */}
          <div className="bg-white dark:bg-border-dark border border-border-light dark:border-border-dark rounded-lg">
            <div className="p-6 border-b border-border-light dark:border-border-dark">
              <div className="flex items-center space-x-2">
                <Bot className="w-5 h-5 text-accent" />
                <h2 className="text-lg font-semibold">AI Recommendations</h2>
              </div>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                {aiRecommendations.map(rec => <div key={rec.id} className="border border-border-light dark:border-border-dark rounded-lg p-4">
                    <div className="flex items-start justify-between mb-2">
                      <h4 className="font-medium text-sm">{rec.title}</h4>
                      <span className={`px-2 py-1 text-xs rounded-full ${rec.priority === 'high' ? 'bg-danger/10 text-danger' : rec.priority === 'medium' ? 'bg-yellow-500/10 text-yellow-600' : 'bg-accent/10 text-accent'}`}>
                        {rec.priority}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                      {rec.message}
                    </p>
                    <button className="text-accent hover:text-accent/80 text-sm font-medium">
                      {rec.action}
                    </button>
                  </div>)}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>;
}