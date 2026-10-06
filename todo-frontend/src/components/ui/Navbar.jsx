import React from 'react';
import { CheckSquare2, User, LogOut } from 'lucide-react';
import Button from './Button';

export default function Navbar({ user, onLogout }) {
  return (
    <nav className="sticky top-0 z-40 border-b border-blue-100 bg-white/85 backdrop-blur">
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-4 sm:px-6">
        <div className="flex items-center gap-7">
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-blue-600 to-indigo-600 text-white shadow-sm shadow-blue-900/20">
              <CheckSquare2 className="h-4 w-4" />
            </div>
            <span className="text-sm font-bold text-slate-950">
              Todo<span className="text-blue-600">Flow</span>
            </span>
          </div>

          <span className="hidden rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700 sm:inline">Dashboard</span>
        </div>

        <div className="flex items-center gap-3">
          <div className="hidden max-w-[220px] items-center gap-2 rounded-md border border-emerald-100 bg-emerald-50 px-2.5 py-1.5 md:flex">
            <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-md bg-white text-emerald-600 shadow-sm">
              <User className="h-3.5 w-3.5" />
            </div>
            <span className="truncate text-xs font-medium text-emerald-800">{user?.email || 'Signed in'}</span>
          </div>

          <Button variant="ghost" size="sm" onClick={onLogout} aria-label="Log out">
            <LogOut className="h-4 w-4" />
            <span className="hidden sm:inline">Logout</span>
          </Button>
        </div>
      </div>
    </nav>
  );
}
