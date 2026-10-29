import React, { useEffect, useState } from 'react';
import { AlertCircle, CheckCircle, X } from 'lucide-react';

// English: Browser events keep Redux/API logic separate from visual notifications.
// Roman Urdu: Browser events Redux/API logic ko visual notifications se alag rakhte hain.
export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  useEffect(() => {
    const handleToastEvent = (event) => {
      const id = crypto.randomUUID?.() || Math.random().toString(36).slice(2);
      const nextToast = { id, ...event.detail };
      setToasts((current) => [...current, nextToast]);

      // English: Remove each toast automatically after 3.5 seconds.
      // Roman Urdu: Har toast 3.5 seconds ke baad automatically remove hota hai.
      window.setTimeout(() => setToasts((current) => current.filter((item) => item.id !== id)), 3500);
    };
    window.addEventListener('app-toast', handleToastEvent);
    return () => window.removeEventListener('app-toast', handleToastEvent);
  }, []);

  return (
    <div className="relative">
      {children}
      <div className="pointer-events-none fixed inset-x-4 bottom-4 z-[60] flex flex-col items-end gap-2 sm:left-auto sm:right-6 sm:w-96" aria-live="polite" aria-atomic="true">
        {toasts.map((item) => (
          <div key={item.id} className="pointer-events-auto flex w-full animate-toast-in items-center gap-3 rounded-2xl border border-[var(--border)] bg-white p-3.5 shadow-xl">
            <span className={['flex h-8 w-8 shrink-0 items-center justify-center rounded-xl', item.type === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'].join(' ')}>
              {item.type === 'success' ? <CheckCircle className="h-4 w-4" /> : <AlertCircle className="h-4 w-4" />}
            </span>
            <span className="flex-1 text-sm font-semibold text-[var(--text-primary)]">{item.message}</span>
            <button onClick={() => setToasts((current) => current.filter((toastItem) => toastItem.id !== item.id))} className="rounded-lg p-1.5 text-[var(--text-muted)] hover:bg-stone-100" aria-label="Dismiss notification">
              <X className="h-4 w-4" />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

export const toast = {
  // English: Any component can dispatch this event without importing provider state.
  // Roman Urdu: Koi bhi component provider state import kiye baghair ye event bhej sakta hai.
  success: (message) => window.dispatchEvent(new CustomEvent('app-toast', { detail: { message, type: 'success' } })),
  error: (message) => window.dispatchEvent(new CustomEvent('app-toast', { detail: { message, type: 'error' } })),
};
