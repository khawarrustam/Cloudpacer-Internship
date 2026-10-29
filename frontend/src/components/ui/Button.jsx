import React from 'react';

// English: forwardRef lets a dialog move keyboard focus to this button.
// Roman Urdu: forwardRef dialog ko keyboard focus is button par lane deta hai.
const Button = React.forwardRef(function Button({
  children,
  variant = 'primary',
  size = 'md',
  className = '',
  isLoading = false,
  disabled = false,
  ...props
}, ref) {
  const variants = {
    primary: 'bg-[var(--primary)] text-white shadow-sm hover:bg-[var(--primary-hover)] hover:-translate-y-px',
    secondary: 'border border-[var(--border)] bg-white text-[var(--text-primary)] hover:border-[var(--border-strong)] hover:bg-stone-50',
    solidDanger: 'bg-[var(--danger)] text-white hover:bg-red-700',
  };
  const sizes = {
    sm: 'h-9 px-3 text-xs',
    md: 'h-10 px-4 text-sm',
    lg: 'h-12 px-5 text-sm',
  };
  // English: Disable the button during loading to prevent duplicate API actions.
  // Roman Urdu: Loading ke waqt button disable hota hai taa-ke duplicate API call na ho.
  const isDisabled = disabled || isLoading;

  return (
    <button
      ref={ref}
      disabled={isDisabled}
      className={[
        'inline-flex items-center justify-center gap-2 rounded-xl font-bold transition duration-200 active:translate-y-0 active:scale-[0.98] disabled:pointer-events-none disabled:opacity-50',
        sizes[size],
        variants[variant],
        className,
      ].join(' ')}
      {...props}
    >
      {isLoading && (
        <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" aria-hidden="true">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.37 0 0 5.37 0 12h4z" />
        </svg>
      )}
      {children}
    </button>
  );
});

export default Button;
