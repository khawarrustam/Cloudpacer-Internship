import React from 'react';

export default function Card({ children, className = '', title, subtitle }) {
  return (
    <section className={`card-surface p-6 ${className}`}>
      {(title || subtitle) && (
        <div className="mb-6 border-b border-[var(--primary)] pb-4">
          {title && <h3 className="text-sm font-black uppercase tracking-widest text-[var(--primary)] shadow-[0_0_5px_var(--primary)]">{title}</h3>}
          {subtitle && <p className="text-xs font-mono text-[var(--text-secondary)] mt-1">{subtitle}</p>}
        </div >
      )}
      {children}
    </section>
  );
}
