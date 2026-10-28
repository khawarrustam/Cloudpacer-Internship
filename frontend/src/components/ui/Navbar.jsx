import React from 'react';
import { Check, LogOut, SunMedium } from 'lucide-react';
import Button from './Button';

export default function Navbar({ user, onLogout }) {
  const email = user?.email || 'Signed in';
  const initial = email.charAt(0).toUpperCase();

  return (
    <nav className="sticky top-0 z-40 border-b border-black/5 bg-white/75 backdrop-blur-xl">
      <div className="mx-auto flex h-[72px] max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-[var(--text-primary)] text-white shadow-sm">
            <Check className="h-5 w-5" strokeWidth={3} />
          </div>
          <div>
            <p className="text-sm font-extrabold tracking-tight">TodoFlow</p>
            <p className="font-mono text-[9px] uppercase tracking-[0.14em] text-[var(--text-muted)]">Personal workspace</p>
          </div>
        </div>

        <div className="flex items-center gap-2 sm:gap-3">
          <div className="hidden items-center gap-2 rounded-full border border-[var(--border)] bg-[var(--bg-main)] px-3 py-2 text-[10px] font-extrabold uppercase tracking-[0.12em] text-[var(--text-secondary)] md:flex">
            <SunMedium className="h-3.5 w-3.5 text-amber-500" />
            Today
            <span className="h-1.5 w-1.5 rounded-full bg-green-500 shadow-[0_0_0_3px_rgba(34,197,94,0.12)]" />
          </div>
          <div className="hidden items-center gap-2.5 rounded-full border border-[var(--border)] bg-white py-1.5 pl-1.5 pr-3 sm:flex">
            <span className="flex h-7 w-7 items-center justify-center rounded-full bg-[var(--primary-soft)] text-xs font-extrabold text-[var(--primary)]">{initial}</span>
            <span className="max-w-44 truncate text-xs font-semibold text-[var(--text-secondary)]">{email}</span>
          </div>
          <Button variant="ghost" size="icon" onClick={onLogout} aria-label="Log out">
            <LogOut className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </nav>
  );
}
