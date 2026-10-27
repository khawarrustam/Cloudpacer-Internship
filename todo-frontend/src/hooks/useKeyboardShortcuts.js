import { useEffect } from 'react';

// English: Keep global keyboard shortcuts away from visual components.
// Roman Urdu: Global shortcuts ko UI component se alag rakha gaya hai.
export function useKeyboardShortcuts() {
  useEffect(() => {
    const handleKeyDown = (event) => {
      const target = event.target;
      const isTyping = ['INPUT', 'TEXTAREA', 'SELECT'].includes(target.tagName)
        || target.isContentEditable;

      if (isTyping) return;

      if (event.key === '/') {
        event.preventDefault();
        document.getElementById('task-search')?.focus();
      }

      if (event.key.toLowerCase() === 'n') {
        event.preventDefault();
        document.getElementById('new-task-title')?.focus();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);
}
