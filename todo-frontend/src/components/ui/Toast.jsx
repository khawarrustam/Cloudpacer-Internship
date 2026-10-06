import React, { useState, useEffect } from 'react';
import { CheckCircle, AlertCircle, X } from 'lucide-react';

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const addToast = (message, type = 'success', duration = 3000) => {
    const id = Math.random().toString(36).substr(2, 9);
    setToasts(prev => [...prev, { id, message, type }]);
    
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, duration);
  };

  // We use a simple window event to trigger toasts from anywhere in the app
  useEffect(() => {
    const handleToastEvent = (e) => {
      const { message, type } = e.detail;
      addToast(message, type);
    };
    window.addEventListener('app-toast', handleToastEvent);
    return () => window.removeEventListener('app-toast', handleToastEvent);
  }, []);

  return (
    <div className="relative">
      {children}
      <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-3 pointer-events-none">
        {toasts.map(toast => (
          <div 
            key={toast.id} 
            className="pointer-events-auto animate-in slide-in-from-right-full flex items-center gap-3 px-4 py-3 rounded-xl shadow-lg border min-w-[300px] bg-white transition-all duration-300"
            style={{ 
              borderColor: toast.type === 'success' ? 'var(--success)' : 'var(--danger)',
              borderLeftWidth: '4px'
            }}
          >
            {toast.type === 'success' ? (
              <CheckCircle className="w-5 h-5 text-emerald-500" />
            ) : (
              <AlertCircle className="w-5 h-5 text-red-500" />
            )}
            <span className="text-sm font-medium text-slate-700">{toast.message}</span>
            <button 
              onClick={() => setToasts(prev => prev.filter(t => t.id !== toast.id))}
              className="ml-auto p-1 hover:bg-slate-100 rounded-md transition-colors"
            >
              <X className="w-4 h-4 text-slate-400" />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

export const toast = {
  success: (msg) => window.dispatchEvent(new CustomEvent('app-toast', { detail: { message: msg, type: 'success' } })),
  error: (msg) => window.dispatchEvent(new CustomEvent('app-toast', { detail: { message: msg, type: 'error' } })),
};
