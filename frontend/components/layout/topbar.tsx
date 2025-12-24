'use client';

import { Bell, User } from 'lucide-react';

export default function TopBar() {
  return (
    <div className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-8">
      <div />
      <div className="flex items-center gap-4">
        <button className="p-2 hover:bg-slate-100 rounded-lg transition-colors">
          <Bell className="h-5 w-5 text-slate-600" />
        </button>
        <button className="p-2 hover:bg-slate-100 rounded-lg transition-colors">
          <User className="h-5 w-5 text-slate-600" />
        </button>
      </div>
    </div>
  );
}
