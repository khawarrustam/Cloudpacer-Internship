import React from 'react';

// The generated ID connects the label and help text for screen-reader users.
export default function Input({ label, error, hint, icon: Icon, ...props }) {
  const inputId = props.id || props.name || label?.toLowerCase().replace(/\s+/g, '-');

  return (
    <div className="flex w-full flex-col gap-2">
      {label && (
        <label htmlFor={inputId} className="text-xs font-bold text-[var(--text-primary)]">
          {label}
        </label>
      )}
      <div className="relative">
        {Icon && (
          <Icon className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--text-muted)]" aria-hidden="true" />
        )}
        <input
          id={inputId}
          aria-invalid={Boolean(error)}
          aria-describedby={error ? inputId + '-error' : hint ? inputId + '-hint' : undefined}
          className={['input-base', Icon ? 'pl-10' : '', error ? 'border-red-400 focus:border-red-500 focus:ring-red-500/10' : ''].join(' ')}
          {...props}
        />
      </div>
      {error ? (
        <span id={inputId + '-error'} className="text-xs font-semibold text-[var(--danger)]">{error}</span>
      ) : hint ? (
        <span id={inputId + '-hint'} className="text-xs text-[var(--text-muted)]">{hint}</span>
      ) : null}
    </div>
  );
}
