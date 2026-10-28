import React from 'react';

// Reusable surface with an optional header keeps dashboard sections visually uniform.
export default function Card({ children, className = '', title, subtitle, action }) {
  return (
    <section className={['card-surface p-5 sm:p-6', className].join(' ')}>
      {(title || subtitle || action) && (
        <div className="mb-6 flex items-start justify-between gap-4">
          <div>
            {title && <h3 className="text-base font-extrabold tracking-tight">{title}</h3>}
            {subtitle && <p className="mt-1 text-xs leading-5 text-[var(--text-secondary)]">{subtitle}</p>}
          </div>
          {action}
        </div>
      )}
      {children}
    </section>
  );
}
