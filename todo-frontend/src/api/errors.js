// English: Read a useful message from an API error.
// Roman Urdu: API error se seedha aur samajh aane wala message nikalo.
export function getApiErrorMessage(error, fallback) {
  return error.response?.data?.detail || fallback;
}

export function getTodoErrorMessage(error, fallback) {
  const status = error.response?.status;

  if (status === 401) {
    return 'Session expired. Please log in again.';
  }

  if (status === 403) {
    return 'You do not have permission to access these tasks.';
  }

  return getApiErrorMessage(error, fallback);
}
