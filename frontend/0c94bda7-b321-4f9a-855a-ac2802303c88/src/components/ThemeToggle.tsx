import React, { useEffect, useState } from 'react';
import { Sun, Moon } from 'lucide-react';
export function ThemeToggle() {
  const [isDark, setIsDark] = useState(false);
  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDark]);
  return <button onClick={() => setIsDark(!isDark)} className="w-8 h-8 flex items-center justify-center rounded-sm hover:bg-background-light dark:hover:bg-border-dark">
      {isDark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
    </button>;
}