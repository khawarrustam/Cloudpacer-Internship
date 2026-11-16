import { useEffect, useRef, useState } from 'react';
import { Github, Loader2 } from 'lucide-react';
import { readGitHubCallback } from '../features/auth/githubOAuth';


export default function GitHubCallback({ onLogin }) {
  const started = useRef(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (started.current) return;
    started.current = true;

    async function finishLogin() {
      try {
        // Query pehle memory mein lo, phir code ko address bar se foran hatao.
        const callbackSearch = window.location.search;
        window.history.replaceState({}, '', '/auth/github/callback');
        const code = readGitHubCallback(callbackSearch);
        const result = await onLogin(code);
        if (!result.success) throw new Error(result.error);
        window.history.replaceState({}, '', '/');
      } catch (callbackError) {
        setError(callbackError.message || String(callbackError));
      }
    }

    finishLogin();
  }, [onLogin]);

  return (
    <main className="flex min-h-screen items-center justify-center px-4">
      <section className="w-full max-w-sm rounded-2xl border border-[var(--border)] bg-white p-8 text-center shadow-[var(--shadow-md)]">
        <span className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-[#24292f] text-white">
          <Github className="h-6 w-6" aria-hidden="true" />
        </span>
        <h1 className="mt-5 text-xl font-extrabold">Finishing GitHub login</h1>
        {error ? (
          <>
            <p role="alert" className="mt-3 text-sm text-[var(--danger)]">{error}</p>
            <a href="/" className="mt-5 inline-block text-sm font-bold text-[var(--primary)]">
              Return to sign in
            </a>
          </>
        ) : (
          <p className="mt-3 flex items-center justify-center gap-2 text-sm text-[var(--text-secondary)]">
            <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
            Verifying your account…
          </p>
        )}
      </section>
    </main>
  );
}
