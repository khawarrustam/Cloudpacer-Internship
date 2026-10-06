import React from 'react';

export default function StatsCard({ label, value, color = 'indigo', icon: Icon }) {
  const colors = {
    indigo: 'text-indigo-700 bg-indigo-100 border-indigo-200',
    blue: 'text-blue-700 bg-blue-100 border-blue-200',
    emerald: 'text-emerald-700 bg-emerald-100 border-emerald-200',
    violet: 'text-violet-700 bg-violet-100 border-violet-200',
    slate: 'text-sky-700 bg-sky-100 border-sky-200',
  };

  const rings = {
    indigo: 'hover:border-indigo-200 hover:shadow-indigo-900/10',
    blue: 'hover:border-blue-200 hover:shadow-blue-900/10',
    emerald: 'hover:border-emerald-200 hover:shadow-emerald-900/10',
    violet: 'hover:border-violet-200 hover:shadow-violet-900/10',
    slate: 'hover:border-sky-200 hover:shadow-sky-900/10',
  };

  return (
    <div className={`flex items-center justify-between rounded-xl border border-white/70 bg-white/90 p-4 shadow-sm backdrop-blur transition-all hover:-translate-y-0.5 hover:shadow-md ${rings[color]}`}>
      <div>
        <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">{label}</p>
        <p className="text-2xl font-black text-slate-800">{value}</p>
      </div>
      <div className={`h-10 w-10 rounded-lg border flex items-center justify-center ${colors[color]}`}>
        {Icon ? <Icon className="w-5 h-5" /> : <div className="w-2 h-2 rounded-full bg-current" />}
      </div>
    </div>
  );
}
