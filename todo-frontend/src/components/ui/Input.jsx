import React from 'react';

export default function Input({ label, error, icon: Icon, ...props }) {
  const inputId = props.id || props.name || label?.toLowerCase().replace(/\s+/g, '-');

  return (
    <div className="flex flex-col gap-2 w-full">
      {label && (
        <label htmlFor={inputId} className="text-xs font-bold uppercase tracking-wider text-[var(--text-secondary)]">
          {label}
        </label>
      )}
      <div className="relative">
        {Icon && (
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--text-muted)]">
            <Icon className="w-4 h-4" />
          </div>
        )}
        <input
          id={inputId}
          aria-invalid={Boolean(error)}
          aria-describedby={error ? `${inputId}-error` : undefined}
          className={`input-base ${Icon ? 'pl-10' : 'px-4'} ${error ? 'border-[var(--danger)] focus:ring-[var(--danger)]/20' : ''}`}
          {...props}
        />
      </div >
      {error && (
        <span id={`${inputId}-error`} className="text-xs font-medium text-[var(--danger)] animate-in fade-in slide-in-from-top-1">
          {error}
        </span>
      )}
    </div >
  );
}
