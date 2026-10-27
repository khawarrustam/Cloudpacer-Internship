const TOKEN_KEY = 'auth_token';
const USER_ID_KEY = 'user_uid';
const USER_EMAIL_KEY = 'user_email';

// English: Keep browser storage code in one file.
// Roman Urdu: Browser storage ka sara code aik file mein rakha gaya hai.
export function readStoredUser() {
  const token = localStorage.getItem(TOKEN_KEY);
  const uid = localStorage.getItem(USER_ID_KEY);
  const email = localStorage.getItem(USER_EMAIL_KEY);

  return token && uid ? { uid, email: email || '' } : null;
}

export function saveSession(data) {
  localStorage.setItem(TOKEN_KEY, data.token);
  localStorage.setItem(USER_ID_KEY, data.uid);
  localStorage.setItem(USER_EMAIL_KEY, data.email || '');
}

export function clearSession() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_ID_KEY);
  localStorage.removeItem(USER_EMAIL_KEY);
}

export function readToken() {
  return localStorage.getItem(TOKEN_KEY);
}
