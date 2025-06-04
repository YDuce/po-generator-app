import React from 'react';
import { ArrowLeft, ExternalLink, Settings, TrendingUp, Package, DollarSign } from 'lucide-react';
interface ChannelViewProps {
  channel: any;
  onBack: () => void;
}
export function ChannelView({
  channel,
  onBack
}: ChannelViewProps) {
  const channelMetrics = [{
    label: 'Active Listings',
    value: channel.products,
    change: '+12',
    icon: Package
  }, {
    label: 'Monthly Revenue',
    value: channel.revenue,
    change: channel.change,
    icon: DollarSign
  }, {
    label: 'Avg. Rating',
    value: '4.3/5',
    change: '+0.2',
    icon: TrendingUp
  }, {
    label: 'Performance',
    value: '84%',
    change: '+5%',
    icon: TrendingUp
  }];
  return <div className="p-6 bg-background-light dark:bg-background-dark min-h-screen w-full">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button onClick={onBack} className="flex items-center justify-center w-10 h-10 rounded-lg border border-border-light dark:border-border-dark hover:bg-white dark:hover:bg-border-dark transition-colors">
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div>
              <h1 className="text-2xl font-semibold">{channel.name}</h1>
              <p className="text-gray-500 dark:text-gray-400 mt-1">
                Channel-specific management and analytics
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <button className="flex items-center space-x-2 px-4 py-2 text-sm border border-border-light dark:border-border-dark rounded-lg hover:bg-white dark:hover:bg-border-dark transition-colors">
              <Settings className="w-4 h-4" />
              <span>Manage Channel</span>
            </button>
            <button className="flex items-center space-x-2 px-4 py-2 text-sm bg-accent text-white rounded-lg hover:bg-accent/90 transition-colors">
              <ExternalLink className="w-4 h-4" />
              <span>View on {channel.name}</span>
            </button>
          </div>
        </div>
        {/* Channel Status */}
        <div className="bg-white dark:bg-border-dark border border-border-light dark:border-border-dark rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className={`w-3 h-3 rounded-full ${channel.status === 'Connected' ? 'bg-success' : 'bg-yellow-500'}`} />
              <span className="font-medium">{channel.status}</span>
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400">
              Last sync: {channel.lastSync}
            </div>
          </div>
        </div>
        {/* Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {channelMetrics.map(metric => {
          const Icon = metric.icon;
          return <div key={metric.label} className="bg-white dark:bg-border-dark border border-border-light dark:border-border-dark rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <Icon className="w-5 h-5 text-accent" />
                  <span className={`text-sm font-medium ${metric.change.startsWith('+') ? 'text-success' : 'text-gray-500'}`}>
                    {metric.change}
                  </span>
                </div>
                <div className="space-y-1">
                  <p className="text-2xl font-bold">{metric.value}</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {metric.label}
                  </p>
                </div>
              </div>;
        })}
        </div>
        {/* Channel-specific content placeholder */}
        <div className="bg-white dark:bg-border-dark border border-border-light dark:border-border-dark rounded-lg p-8 text-center">
          <Package className="w-12 h-12 text-accent mx-auto mb-4" />
          <h3 className="text-lg font-semibold mb-2">Channel Details</h3>
          <p className="text-gray-500 dark:text-gray-400">
            Detailed {channel.name} management interface coming soon
          </p>
        </div>
      </div>
    </div>;
}