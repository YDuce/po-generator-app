import React from 'react';
import { Clock, AlertTriangle, Activity } from 'lucide-react';
export function DashboardV2() {
  const recentActivity = [{
    id: 1,
    message: 'PO #1234 updated',
    time: '2m ago',
    type: 'update'
  }, {
    id: 2,
    message: 'New PORF generated',
    time: '15m ago',
    type: 'create'
  }, {
    id: 3,
    message: 'Inventory alert: Low stock',
    time: '1h ago',
    type: 'alert'
  }];
  const expiringPOs = [{
    id: 'PO-123',
    supplier: 'TechSupply Inc',
    daysLeft: 5,
    status: 'pending'
  }, {
    id: 'PO-124',
    supplier: 'Global Electronics',
    daysLeft: 7,
    status: 'partial'
  }, {
    id: 'PO-125',
    supplier: 'ABC Vendors',
    daysLeft: 10,
    status: 'pending'
  }];
  return <div className="p-6 bg-background-light dark:bg-background-dark min-h-screen">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* KPI Chart */}
        <div className="lg:col-span-2 bg-white dark:bg-border-dark border border-border-light dark:border-border-dark rounded-sm p-card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">Units Sold</h2>
            <select className="text-sm border border-border-light dark:border-border-dark rounded-sm px-2 py-1 bg-transparent">
              <option>Last 7 days</option>
              <option>Last 30 days</option>
              <option>Last 90 days</option>
            </select>
          </div>
          <div className="h-[300px] flex items-center justify-center border-t border-border-light dark:border-border-dark">
            <Activity className="w-6 h-6 text-accent" />
            <span className="ml-2 text-sm">Chart placeholder</span>
          </div>
        </div>
        {/* Expiring POs */}
        <div className="bg-white dark:bg-border-dark border border-border-light dark:border-border-dark rounded-sm p-card">
          <h2 className="text-xl font-semibold mb-4">Expiring POs</h2>
          <div className="space-y-4">
            {expiringPOs.map(po => <div key={po.id} className="flex items-start space-x-3 pb-4 border-b border-border-light dark:border-border-dark last:border-0 last:pb-0">
                <div className="p-2 bg-background-light dark:bg-background-dark rounded-sm">
                  <Clock className="w-4 h-4 text-accent" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <span className="font-medium">{po.id}</span>
                    <span className={`text-sm ${po.daysLeft <= 5 ? 'text-danger' : 'text-success'}`}>
                      {po.daysLeft}d left
                    </span>
                  </div>
                  <span className="text-sm text-gray-500 dark:text-gray-400">
                    {po.supplier}
                  </span>
                </div>
              </div>)}
          </div>
        </div>
        {/* Recent Activity */}
        <div className="lg:col-span-2 bg-white dark:bg-border-dark border border-border-light dark:border-border-dark rounded-sm p-card">
          <h2 className="text-xl font-semibold mb-4">Recent Activity</h2>
          <div className="space-y-4">
            {recentActivity.map(activity => <div key={activity.id} className="flex items-start space-x-3 pb-4 border-b border-border-light dark:border-border-dark last:border-0 last:pb-0">
                <div className="p-2 bg-background-light dark:bg-background-dark rounded-sm">
                  <Activity className="w-4 h-4 text-accent" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <span className="font-medium">{activity.message}</span>
                    <span className="text-sm text-gray-500 dark:text-gray-400">
                      {activity.time}
                    </span>
                  </div>
                </div>
              </div>)}
          </div>
        </div>
        {/* Settings Preview */}
        <div className="bg-white dark:bg-border-dark border border-border-light dark:border-border-dark rounded-sm p-card">
          <h2 className="text-xl font-semibold mb-4">AI Assistant</h2>
          <div className="p-4 bg-background-light dark:bg-background-dark rounded-sm border border-border-light dark:border-border-dark text-center">
            <AlertTriangle className="w-6 h-6 text-accent mx-auto mb-2" />
            <p className="text-sm text-gray-500 dark:text-gray-400">
              AI assistant coming soon
            </p>
          </div>
        </div>
      </div>
    </div>;
}