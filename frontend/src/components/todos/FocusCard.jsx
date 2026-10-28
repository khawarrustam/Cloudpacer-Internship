import React from 'react';
import { Command, Target } from 'lucide-react';
import Card from '../ui/Card';

// Derive encouraging copy from existing progress instead of storing duplicate UI state.
export default function FocusCard({ progress, pending, hasTodos }) {
  const title = progress === 100 && hasTodos
    ? 'Make room for tomorrow.'
    : progress >= 50
      ? 'Protect your momentum.'
      : 'Start with the smallest win.';

  return (
    <Card className="overflow-hidden">
      <div className="rounded-2xl bg-[var(--primary-soft)] p-4">
        <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-white text-[var(--primary)] shadow-sm">
          <Target className="h-4 w-4" />
        </span>
        <p className="mt-4 font-mono text-[9px] font-medium uppercase tracking-[0.16em] text-[var(--primary)]">Focus note</p>
        <h3 className="mt-2 text-sm font-extrabold">{title}</h3>
        <p className="mt-1 text-xs leading-5 text-[var(--text-secondary)]">
          {pending
            ? 'Pick one open task and finish it before adding more.'
            : 'Your list is clear. Enjoy the space you made.'}
        </p>
      </div>
      <div className="mt-4 flex items-center justify-between text-[10px] font-bold text-[var(--text-muted)]">
        <span className="flex items-center gap-1.5"><Command className="h-3.5 w-3.5" />Shortcuts</span>
        <span><kbd className="font-mono">/</kbd> search · <kbd className="font-mono">N</kbd> new</span>
      </div>
    </Card>
  );
}
