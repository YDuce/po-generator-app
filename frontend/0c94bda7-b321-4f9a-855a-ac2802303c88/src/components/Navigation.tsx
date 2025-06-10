import React from 'react';
import { UserCircle } from 'lucide-react';
export function Navigation() {
  return <header className="h-14 border-b border-border-light dark:border-border-dark bg-white dark:bg-border-dark flex items-center px-4 justify-between">
      <div className="flex items-center space-x-4">
        <h1 className="text-lg font-semibold">Seller Hub</h1>
      </div>
      <div className="flex items-center space-x-4">
        <button className="w-8 h-8 flex items-center justify-center rounded-sm hover:bg-background-light dark:hover:bg-border-dark">
          <UserCircle className="w-5 h-5" />
        </button>
      </div>
    </header>;
}