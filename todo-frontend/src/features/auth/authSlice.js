import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { authApi } from '../../api/authApi';

function readStoredUser() {
  const token = localStorage.getItem('auth_token');
  const uid = localStorage.getItem('user_uid');
  const email = localStorage.getItem('user_email');

  return token && uid ? { uid, email: email || '' } : null;
}

function saveSession(data) {
  localStorage.setItem('auth_token', data.token);
  localStorage.setItem('user_uid', data.uid);
  localStorage.setItem('user_email', data.email || '');
}

function clearSession() {
  localStorage.removeItem('auth_token');
  localStorage.removeItem('user_uid');
  localStorage.removeItem('user_email');
}

function getErrorMessage(error, fallback) {
  return error.response?.data?.detail || fallback;
}

export const loginUser = createAsyncThunk(
  'auth/loginUser',
  async ({ email, password }, { rejectWithValue }) => {
    try {
      const data = await authApi.login({ email, password });
      saveSession(data);
      return { uid: data.uid, email: data.email || email };
    } catch (error) {
      return rejectWithValue(
        getErrorMessage(error, 'Login failed. Please check your credentials.'),
      );
    }
  },
);

export const signupUser = createAsyncThunk(
  'auth/signupUser',
  async ({ email, password, displayName }, { rejectWithValue }) => {
    try {
      const data = await authApi.signup({
        email,
        password,
        display_name: displayName,
      });
      saveSession(data);
      return { uid: data.uid, email: data.email || email };
    } catch (error) {
      return rejectWithValue(getErrorMessage(error, 'Signup failed'));
    }
  },
);

const initialState = {
  user: readStoredUser(),
  status: 'idle',
  error: null,
};

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    loggedOut(state) {
      state.user = null;
      state.status = 'idle';
      state.error = null;
    },
    sessionExpired(state) {
      state.user = null;
      state.status = 'idle';
      state.error = 'Your session expired. Please sign in again.';
    },
    clearAuthError(state) {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(loginUser.pending, (state) => {
        state.status = 'loading';
        state.error = null;
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.user = action.payload;
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload || action.error.message;
      })
      .addCase(signupUser.pending, (state) => {
        state.status = 'loading';
        state.error = null;
      })
      .addCase(signupUser.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.user = action.payload;
      })
      .addCase(signupUser.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload || action.error.message;
      });
  },
});

export const { loggedOut, sessionExpired, clearAuthError } = authSlice.actions;

export const logoutUser = () => (dispatch) => {
  clearSession();
  dispatch(loggedOut());
};

export const expireSession = () => (dispatch) => {
  clearSession();
  dispatch(sessionExpired());
};

export const selectCurrentUser = (state) => state.auth.user;
export const selectIsAuthenticated = (state) => Boolean(state.auth.user);
export const selectAuthStatus = (state) => state.auth.status;
export const selectAuthError = (state) => state.auth.error;

export default authSlice.reducer;
