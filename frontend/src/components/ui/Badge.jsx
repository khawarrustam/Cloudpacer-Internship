import React from 'react';

export default function Badge({ children, variant = 'default', className = '' }) {
  const variants = {
    default: 'border-stone-200 bg-stone-100 text-stone-600',
    success: 'border-green-200 bg-green-50 text-green-700',
    warning: 'border-amber-200 bg-amber-50 text-amber-700',
    danger: 'border-red-200 bg-red-50 text-red-700',
    primary: 'border-blue-200 bg-blue-50 text-blue-700',
  };

  return (
    <span className={['inline-flex items-center gap-1 rounded-full border px-2.5 py-1 text-[10px] font-extrabold uppercase tracking-[0.1em]', variants[variant], className].join(' ')}>
      {children}
    </span>
  );
}
