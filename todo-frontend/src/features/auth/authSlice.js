import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { authApi } from '../../api/authApi';
import { getApiErrorMessage } from '../../api/errors';
import { clearSession, readStoredUser, saveSession } from './authStorage';

// English: A thunk runs async work, then Redux sends pending/fulfilled/rejected.
// Roman Urdu: Thunk async kaam karta hai, phir Redux request ka result bhejta hai.
export const loginUser = createAsyncThunk(
  'auth/loginUser',
  async ({ email, password }, { rejectWithValue }) => {
    try {
      const data = await authApi.login({ email, password });
      saveSession(data);
      return { uid: data.uid, email: data.email || email };
    } catch (error) {
      return rejectWithValue(
        getApiErrorMessage(
          error,
          'Login failed. Please check your credentials.',
        ),
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
      return rejectWithValue(
        getApiErrorMessage(error, 'Signup failed'),
      );
    }
  },
);

const initialState = {
  // English: Reloading the page keeps a valid saved user.
  // Roman Urdu: Page reload par valid saved user dobara mil jata hai.
  user: readStoredUser(),
  status: 'idle',
};

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    // English: Normal reducers handle immediate, non-API changes.
    // Roman Urdu: Normal reducers foran honay wali non-API changes handle karte hain.
    loggedOut(state) {
      state.user = null;
      state.status = 'idle';
    },
    sessionExpired(state) {
      state.user = null;
      state.status = 'idle';
    },
  },
  extraReducers: (builder) => {
    // English: extraReducers handles the async thunk results.
    // Roman Urdu: extraReducers async thunk ke results handle karta hai.
    builder
      .addCase(loginUser.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.user = action.payload;
      })
      .addCase(loginUser.rejected, (state) => {
        state.status = 'failed';
      })
      .addCase(signupUser.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(signupUser.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.user = action.payload;
      })
      .addCase(signupUser.rejected, (state) => {
        state.status = 'failed';
      });
  },
});

export const { loggedOut, sessionExpired } = authSlice.actions;

export const logoutUser = () => (dispatch) => {
  // English: Clear browser storage first, then clear Redux.
  // Roman Urdu: Pehle browser storage, phir Redux clear karo.
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

export default authSlice.reducer;
