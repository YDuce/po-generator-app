import React, { useState } from 'react';
import { Navigation } from './components/Navigation';
import { ModernDashboard } from './components/ModernDashboard';
import { ChannelView } from './components/ChannelView';
import { ThemeToggle } from './components/ThemeToggle';
import { LayoutDashboard, Package, BarChart3, Calendar, Settings, Users, LogOut } from 'lucide-react';
export function App() {
  const [activeView, setActiveView] = useState('dashboard');
  const [selectedChannel, setSelectedChannel] = useState(null);
  const sidebarItems = [{
    id: 'dashboard',
    label: 'Dashboard',
    icon: LayoutDashboard
  }, {
    id: 'inventory',
    label: 'Inventory',
    icon: Package
  }, {
    id: 'analytics',
    label: 'Analytics',
    icon: BarChart3
  }, {
    id: 'events',
    label: 'Events',
    icon: Calendar
  }, {
    id: 'settings',
    label: 'Settings',
    icon: Settings
  }, {
    id: 'team',
    label: 'Team',
    icon: Users
  }];
  return <div className="min-h-screen bg-background-light dark:bg-background-dark text-gray-900 dark:text-gray-100 w-full">
      <Navigation />
      <div className="flex w-full">
        {/* Sidebar */}
        <aside className="w-16 border-r border-border-light dark:border-border-dark bg-white dark:bg-border-dark flex flex-col items-center py-6 space-y-6">
          {sidebarItems.map(item => {
          const Icon = item.icon;
          return <button key={item.id} onClick={() => {
            setActiveView(item.id);
            setSelectedChannel(null);
          }} className={`w-10 h-10 flex items-center justify-center rounded-lg transition-colors ${activeView === item.id ? 'bg-accent text-white' : 'hover:bg-background-light dark:hover:bg-background-dark text-gray-600 dark:text-gray-400'}`} title={item.label}>
                <Icon className="w-5 h-5" />
              </button>;
        })}
          <div className="mt-auto space-y-4">
            <ThemeToggle />
            <button className="w-10 h-10 flex items-center justify-center rounded-lg hover:bg-background-light dark:hover:bg-background-dark text-gray-600 dark:text-gray-400">
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        </aside>
        {/* Main Content */}
        <main className="flex-1 w-full">
          {selectedChannel ? <ChannelView channel={selectedChannel} onBack={() => setSelectedChannel(null)} /> : <ModernDashboard activeView={activeView} onChannelSelect={setSelectedChannel} />}
        </main>
      </div>
    </div>;
}