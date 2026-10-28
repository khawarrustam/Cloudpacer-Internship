import React, { useEffect, useRef } from 'react';
import { AlertTriangle, X } from 'lucide-react';
import Button from './Button';

export default function ConfirmModal({
  open,
  title,
  description,
  confirmLabel = 'Delete task',
  cancelLabel = 'Keep task',
  isLoading = false,
  onConfirm,
  onCancel,
}) {
  const cancelRef = useRef(null);

  useEffect(() => {
    if (!open) return undefined;
    cancelRef.current?.focus();
    const handleKeyDown = (event) => {
      if (event.key === 'Escape' && !isLoading) onCancel();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [open, isLoading, onCancel]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-stone-950/35 p-4 backdrop-blur-sm" onMouseDown={(event) => event.target === event.currentTarget && !isLoading && onCancel()}>
      <div role="alertdialog" aria-modal="true" aria-labelledby="delete-title" aria-describedby="delete-description" className="w-full max-w-md animate-slide-up rounded-3xl border border-white/50 bg-white p-6 shadow-2xl">
        <div className="mb-6 flex items-start gap-4">
          <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-red-50 text-[var(--danger)]">
            <AlertTriangle className="h-5 w-5" />
          </div>
          <div className="min-w-0 flex-1">
            <h2 id="delete-title" className="text-lg font-extrabold tracking-tight">{title}</h2>
            <p id="delete-description" className="mt-1.5 text-sm leading-6 text-[var(--text-secondary)]">{description}</p>
          </div>
          <button type="button" onClick={onCancel} disabled={isLoading} className="rounded-lg p-1 text-[var(--text-muted)] hover:bg-stone-100" aria-label="Close dialog">
            <X className="h-4 w-4" />
          </button>
        </div>
        <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
          <Button ref={cancelRef} type="button" variant="secondary" onClick={onCancel} disabled={isLoading}>{cancelLabel}</Button>
          <Button type="button" variant="solidDanger" onClick={onConfirm} isLoading={isLoading}>{confirmLabel}</Button>
        </div>
      </div>
    </div>
  );
}
