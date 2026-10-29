const TOKEN_KEY = 'auth_token';
const USER_ID_KEY = 'user_uid';
const USER_EMAIL_KEY = 'user_email';

// English: Keep browser storage code in one file.
// Roman Urdu: Browser storage ka sara code aik file mein rakha gaya hai.
export function readStoredUser() {
  // English: Restore only the small user object needed by the UI after a refresh.
  // Roman Urdu: Refresh ke baad UI ke liye zaroori chhota user object restore karo.
  const token = localStorage.getItem(TOKEN_KEY);
  const uid = localStorage.getItem(USER_ID_KEY);
  const email = localStorage.getItem(USER_EMAIL_KEY);

  return token && uid ? { uid, email: email || '' } : null;
}

export function saveSession(data) {
  // English: Save login data so the session survives a browser refresh.
  // Roman Urdu: Login data save karo taa-ke browser refresh ke baad session rahe.
  localStorage.setItem(TOKEN_KEY, data.token);
  localStorage.setItem(USER_ID_KEY, data.uid);
  localStorage.setItem(USER_EMAIL_KEY, data.email || '');
}

export function clearSession() {
  // English: Remove all saved authentication values during logout or expiry.
  // Roman Urdu: Logout ya expiry par tamam saved authentication values remove karo.
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_ID_KEY);
  localStorage.removeItem(USER_EMAIL_KEY);
}

export function readToken() {
  // English: The Axios interceptor reads this token for protected requests.
  // Roman Urdu: Axios interceptor protected requests ke liye ye token read karta hai.
  return localStorage.getItem(TOKEN_KEY);
}
