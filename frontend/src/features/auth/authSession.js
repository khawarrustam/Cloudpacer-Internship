// The token stays in JavaScript memory only. Nothing is saved in localStorage.
// Token sirf JavaScript memory mein rehta hai. localStorage mein kuch save nahi hota.
let token = null;

export function saveSession(data) {
  token = data.token;
}

export function clearSession() {
  token = null;
}

export function readToken() {
  return token;
}
