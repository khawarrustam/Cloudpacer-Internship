import React from 'react';

export default function Button({ 
  children, 
  variant = 'primary', 
  size = 'md',
  className = '', 
  isLoading = false, 
  disabled = false, 
  ...props 
}) {
  const variants = {
    primary: 'bg-[var(--primary)] text-[var(--primary-foreground)] hover:bg-[var(--primary-hover)]',
    secondary: 'bg-white text-[var(--text-primary)] border border-[var(--border)] hover:bg-[var(--bg-muted)]',
    danger: 'bg-white text-[var(--danger)] border border-[var(--border)] hover:bg-red-50',
    solidDanger: 'bg-[var(--danger)] text-white hover:opacity-90',
    ghost: 'bg-transparent text-[var(--text-secondary)] hover:bg-[var(--bg-muted)] hover:text-[var(--text-primary)]',
  };

  const sizes = {
    sm: 'h-8 px-3 text-xs',
    md: 'h-10 px-4 text-sm',
    lg: 'h-12 px-5 text-sm',
    icon: 'h-10 w-10 p-0',
  };

  return (
    <button
      disabled={disabled || isLoading}
      className={`rounded-sm font-bold transition-all duration-100 active:scale-95 flex items-center justify-center gap-2 disabled:opacity-50 disabled:pointer-events-none ${sizes[size]} ${variants[variant]} ${className}`}
      {...props}
    >
      {isLoading ? (
        <svg className="animate-spin h-4 w-4 text-current" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.948l3-2.647z" />
        </svg>
      ) : null}
      {children}
    </button>
  );
}
