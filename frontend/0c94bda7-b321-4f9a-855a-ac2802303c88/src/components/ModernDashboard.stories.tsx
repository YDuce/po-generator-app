import React from 'react';
import { ModernDashboard } from './ModernDashboard';

export default {
  title: 'Pages/Dashboard',
  component: ModernDashboard,
  parameters: {
    layout: 'fullscreen',
  },
};

export const Default = () => (
  <ModernDashboard activeView="dashboard" onChannelSelect={() => {}} />
); 