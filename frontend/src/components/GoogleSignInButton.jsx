import { useEffect, useRef, useState } from 'react';

const GOOGLE_SCRIPT_ID = 'google-identity-services';
const GOOGLE_SCRIPT_URL = 'https://accounts.google.com/gsi/client';

let googleScriptPromise;

function loadGoogleScript() {
  // English: Load Google's official browser library only once.
  // Roman Urdu: Google ki official browser library sirf aik dafa load karo.
  if (window.google?.accounts?.id) {
    return Promise.resolve(window.google);
  }

  if (!googleScriptPromise) {
    googleScriptPromise = new Promise((resolve, reject) => {
      const existingScript = document.getElementById(GOOGLE_SCRIPT_ID);
      const script = existingScript || document.createElement('script');

      const loaded = () => resolve(window.google);
      const failed = () => reject(new Error('Google Sign-In script failed to load.'));

      script.addEventListener('load', loaded, { once: true });
      script.addEventListener('error', failed, { once: true });

      if (!existingScript) {
        script.id = GOOGLE_SCRIPT_ID;
        script.src = GOOGLE_SCRIPT_URL;
        script.async = true;
        script.defer = true;
        document.head.appendChild(script);
      }
    });
  }

  return googleScriptPromise;
}

export default function GoogleSignInButton({ onCredential, onError, disabled }) {
  const buttonRef = useRef(null);
  const onCredentialRef = useRef(onCredential);
  const onErrorRef = useRef(onError);
  const [setupError, setSetupError] = useState('');
  const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;

  // Latest callback props refs mein rakhne se Google button dobara initialize nahi hota.
  useEffect(() => {
    onCredentialRef.current = onCredential;
    onErrorRef.current = onError;
  }, [onCredential, onError]);

  useEffect(() => {
    let active = true;

    async function setupGoogleButton() {
      if (!clientId || clientId.startsWith('replace-with-')) {
        setSetupError('Google login setup pending: add VITE_GOOGLE_CLIENT_ID.');
        return;
      }

      try {
        const google = await loadGoogleScript();
        if (!active || !buttonRef.current || !google?.accounts?.id) return;

        // Google returns an ID token in response.credential; backend verifies it.
        google.accounts.id.initialize({
          client_id: clientId,
          callback: async (response) => {
            if (!response.credential) {
              onErrorRef.current('Google did not return a login credential.');
              return;
            }
            const result = await onCredentialRef.current(response.credential);
            if (!result.success) onErrorRef.current(result.error);
          },
        });
        buttonRef.current.replaceChildren();
        google.accounts.id.renderButton(buttonRef.current, {
          type: 'standard',
          theme: 'outline',
          size: 'large',
          text: 'continue_with',
          shape: 'rectangular',
          width: Math.min(window.innerWidth - 80, 336),
        });
      } catch (error) {
        if (active) setSetupError(error.message);
      }
    }

    setupGoogleButton();
    return () => {
      active = false;
    };
  }, [clientId]);

  if (setupError) {
    return <p className="text-center text-xs text-[var(--text-muted)]">{setupError}</p>;
  }

  return (
    <div
      className={disabled ? 'pointer-events-none flex justify-center opacity-60' : 'flex justify-center'}
      aria-disabled={disabled}
    >
      <div ref={buttonRef} className="max-w-full" />
    </div>
  );
}
