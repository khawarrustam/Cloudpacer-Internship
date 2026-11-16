const GITHUB_STATE_KEY = 'todoflow_github_oauth_state';


function createSecureState() {
  // Random state login-CSRF se callback ko protect karti hai.
  const bytes = new Uint8Array(24);
  window.crypto.getRandomValues(bytes);
  return Array.from(bytes, (value) => value.toString(16).padStart(2, '0')).join('');
}


export function startGitHubOAuth() {
  const clientId = import.meta.env.VITE_GITHUB_CLIENT_ID;
  const redirectUri = import.meta.env.VITE_GITHUB_REDIRECT_URI;
  if (!clientId || clientId.startsWith('replace-with-') || !redirectUri) {
    throw new Error('GitHub login setup pending: add GitHub OAuth settings.');
  }
  if (new URL(redirectUri).origin !== window.location.origin) {
    throw new Error(`Open TodoFlow at ${new URL(redirectUri).origin} for GitHub login.`);
  }

  const state = createSecureState();
  window.sessionStorage.setItem(GITHUB_STATE_KEY, state);
  const parameters = new URLSearchParams({
    client_id: clientId,
    redirect_uri: redirectUri,
    scope: 'read:user user:email',
    state,
  });
  window.location.assign(`https://github.com/login/oauth/authorize?${parameters}`);
}


export function readGitHubCallback(search = window.location.search) {
  const parameters = new URLSearchParams(search);
  const providerError = parameters.get('error_description') || parameters.get('error');
  if (providerError) throw new Error(providerError);

  const code = parameters.get('code');
  const returnedState = parameters.get('state');
  const savedState = window.sessionStorage.getItem(GITHUB_STATE_KEY);
  window.sessionStorage.removeItem(GITHUB_STATE_KEY);

  if (!code) throw new Error('GitHub did not return a login code.');
  if (!returnedState || !savedState || returnedState !== savedState) {
    throw new Error('GitHub login state is invalid. Please try again.');
  }
  return code;
}
