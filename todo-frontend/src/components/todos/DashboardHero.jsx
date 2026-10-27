import React from 'react';
import { Plus } from 'lucide-react';

function getUserName(email = '') {
  const firstPart = (email || 'there').split('@')[0].split(/[._-]/)[0];
  return firstPart.charAt(0).toUpperCase() + firstPart.slice(1);
}

function getGreeting() {
  const hour = new Date().getHours();
  if (hour < 12) return 'Good morning';
  if (hour < 18) return 'Good afternoon';
  return 'Good evening';
}

function getProgressMessage(progress, totalTodos) {
  if (progress === 100 && totalTodos > 0) {
    return 'Perfect finish';
  }

  if (progress >= 50) {
    return 'You are in motion';
  }

  return 'Build some momentum';
}

export default function DashboardHero({ user, stats, progress }) {
  const today = new Intl.DateTimeFormat(undefined, {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
  }).format(new Date());

  // English: Stats are calculated by a Redux selector, not inside this UI.
  // Roman Urdu: Stats Redux selector banata hai, yeh UI nahi banati.
  const progressMessage = getProgressMessage(progress, stats.total);

  return (
    <section className="hero-panel relative mb-8 overflow-hidden rounded-[2rem] px-5 py-6 text-white sm:px-8 sm:py-8 lg:px-10">
      <div className="grid items-stretch gap-8 lg:grid-cols-[minmax(0,1fr)_340px]">
        <div className="flex flex-col justify-between">
          <div>
            <p className="font-mono text-[10px] font-medium uppercase tracking-[0.2em] text-[#aebdff]">{today}</p>
            <h1 className="mt-3 max-w-2xl text-3xl font-extrabold leading-tight tracking-[-0.045em] sm:text-4xl lg:text-[2.65rem]">
              {getGreeting()}, {getUserName(user?.email)}.
            </h1>
            <p className="mt-3 max-w-xl text-sm leading-6 text-white/55">
              Choose the work that matters, clear the noise, and give today a clean finish.
            </p>
          </div>

          <div className="mt-7 flex flex-wrap items-center gap-3">
            <button
              type="button"
              onClick={() => document.getElementById('new-task-title')?.focus()}
              className="inline-flex h-11 items-center gap-2 rounded-xl bg-white px-4 text-xs font-extrabold text-[#171917] transition hover:-translate-y-0.5 hover:bg-[#f1f3ff]"
            >
              <Plus className="h-4 w-4" />
              Add a task
              <kbd className="ml-1 rounded-md bg-black/5 px-1.5 py-0.5 font-mono text-[9px]">N</kbd>
            </button>
            <span className="inline-flex h-11 items-center gap-2 rounded-xl border border-white/10 bg-white/[0.06] px-4 text-xs font-bold text-white/70">
              <span className="h-2 w-2 rounded-full bg-[#a8db9c] shadow-[0_0_0_4px_rgba(168,219,156,0.1)]" />
              {stats.pending === 0
                ? 'All clear'
                : `${stats.pending} ${stats.pending === 1 ? 'task' : 'tasks'} open`}
            </span>
          </div>
        </div>

        <div className="rounded-3xl border border-white/10 bg-white/[0.07] p-5 backdrop-blur-sm sm:p-6">
          <div className="flex items-end justify-between gap-4">
            <div>
              <p className="font-mono text-[9px] uppercase tracking-[0.18em] text-white/45">Daily progress</p>
              <p className="mt-2 text-sm font-bold text-white/85">{progressMessage}</p>
            </div>
            <strong className="text-4xl font-extrabold tracking-[-0.05em]">
              {progress}<span className="text-lg text-white/35">%</span>
            </strong>
          </div>

          <div className="mt-5 h-2 overflow-hidden rounded-full bg-white/10">
            <div className="h-full rounded-full bg-[#a8db9c] transition-all duration-500" style={{ width: `${progress}%` }} />
          </div>

          <div className="mt-5 grid grid-cols-3 divide-x divide-white/10">
            {[
              ['All', stats.total],
              ['Open', stats.pending],
              ['Done', stats.completed],
            ].map(([label, value]) => (
              <div key={label} className="px-3 first:pl-0 last:pr-0">
                <p className="text-lg font-extrabold">{value}</p>
                <p className="mt-0.5 text-[9px] font-bold uppercase tracking-wider text-white/35">{label}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
