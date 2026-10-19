import React from 'react';

export default function StatsCard({ label, value, detail, icon: Icon, tone = 'blue' }) {
  const tones = {
    blue: 'bg-blue-50 text-blue-700',
    green: 'bg-green-50 text-green-700',
    amber: 'bg-amber-50 text-amber-700',
    ink: 'bg-stone-100 text-stone-700',
  };

  return (
    <div className="flex min-w-0 items-center gap-3 rounded-2xl border border-[var(--border)] bg-white p-4 shadow-[var(--shadow-sm)]">
      <div className={['flex h-10 w-10 shrink-0 items-center justify-center rounded-xl', tones[tone]].join(' ')}>
        {Icon && <Icon className="h-[18px] w-[18px]" />}
      </div>
      <div className="min-w-0">
        <p className="truncate text-[11px] font-bold text-[var(--text-secondary)]">{label}</p>
        <div className="flex items-baseline gap-1.5">
          <p className="text-xl font-extrabold tracking-tight">{value}</p>
          {detail && <span className="truncate text-[10px] text-[var(--text-muted)]">{detail}</span>}
        </div>
      </div>
    </div>
  );
}
