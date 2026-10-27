import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { authApi } from '../../api/authApi';
import { getApiErrorMessage } from '../../api/errors';
import { clearSession, readStoredUser, saveSession } from './authStorage';

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
  user: readStoredUser(),
  status: 'idle',
};

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
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
