import { useEffect } from 'react';

// English: This custom hook keeps reusable keyboard behavior outside visual components.
// Roman Urdu: Ye custom hook reusable keyboard behavior ko UI components se alag rakhta hai.
export function useKeyboardShortcuts() {
  // English: An empty dependency array runs this effect once when the component mounts.
  // Roman Urdu: Empty dependency array effect ko component mount par aik dafa chalati hai.
  useEffect(() => {
    // English: This handler receives every keydown event from the browser window.
    // Roman Urdu: Ye handler browser window ka har keydown event receive karta hai.
    const handleKeyDown = (event) => {
      const target = event.target;

      // English: Ignore shortcuts while the user is typing in an editable field.
      // Roman Urdu: Editable field mein typing ke waqt shortcuts ignore karo.
      const isTyping = ['INPUT', 'TEXTAREA', 'SELECT'].includes(target.tagName)
        || target.isContentEditable;

      if (isTyping) return;

      // English: Pressing '/' moves focus to the task search input.
      // Roman Urdu: '/' press karne se focus task search input par jata hai.
      if (event.key === '/') {
        event.preventDefault();
        document.getElementById('task-search')?.focus();
      }

      // English: Pressing 'n' moves focus to the new-task title input.
      // Roman Urdu: 'n' press karne se focus new-task title input par jata hai.
      if (event.key.toLowerCase() === 'n') {
        event.preventDefault();
        document.getElementById('new-task-title')?.focus();
      }
    };

    // English: Register on mount and remove on unmount to avoid duplicate listeners.
    // Roman Urdu: Mount par listener add aur unmount par remove hota hai taa-ke duplicate na bane.
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);
}
