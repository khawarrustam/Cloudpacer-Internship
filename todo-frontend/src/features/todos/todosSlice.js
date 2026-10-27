import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { getTodoErrorMessage } from '../../api/errors';
import { todoApi } from '../../api/todoApi';
import { loggedOut, sessionExpired } from '../auth/authSlice';

export const fetchTodos = createAsyncThunk(
  'todos/fetchTodos',
  async (_, { rejectWithValue }) => {
    try {
      return await todoApi.getAll();
    } catch (error) {
      return rejectWithValue(
        getTodoErrorMessage(
          error,
          'Unable to connect to the server. Is the backend running?',
        ),
      );
    }
  },
  {
    condition: (_, { getState }) => (
      getState().todos.fetchStatus !== 'loading'
    ),
  },
);

export const createTodo = createAsyncThunk(
  'todos/createTodo',
  async ({ title, priority }, { rejectWithValue }) => {
    try {
      return await todoApi.create({ title, priority });
    } catch (error) {
      return rejectWithValue(
        getTodoErrorMessage(error, 'Failed to add todo'),
      );
    }
  },
);

export const completeTodo = createAsyncThunk(
  'todos/completeTodo',
  async (id, { rejectWithValue }) => {
    try {
      return await todoApi.complete(id);
    } catch (error) {
      return rejectWithValue(
        getTodoErrorMessage(error, 'Failed to complete todo'),
      );
    }
  },
);

export const deleteTodo = createAsyncThunk(
  'todos/deleteTodo',
  async (id, { rejectWithValue }) => {
    try {
      await todoApi.delete(id);
      return id;
    } catch (error) {
      return rejectWithValue(
        getTodoErrorMessage(error, 'Failed to delete todo'),
      );
    }
  },
);

const initialState = {
  items: [],
  fetchStatus: 'idle',
  createStatus: 'idle',
  completingIds: {},
  deletingIds: {},
  fetchError: null,
};

const todosSlice = createSlice({
  name: 'todos',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchTodos.pending, (state) => {
        state.fetchStatus = 'loading';
        state.fetchError = null;
      })
      .addCase(fetchTodos.fulfilled, (state, action) => {
        state.fetchStatus = 'succeeded';
        state.items = action.payload;
      })
      .addCase(fetchTodos.rejected, (state, action) => {
        state.fetchStatus = 'failed';
        state.fetchError = action.payload || action.error.message;
      })
      .addCase(createTodo.pending, (state) => {
        state.createStatus = 'loading';
      })
      .addCase(createTodo.fulfilled, (state, action) => {
        state.createStatus = 'succeeded';
        state.items.push(action.payload);
      })
      .addCase(createTodo.rejected, (state) => {
        state.createStatus = 'failed';
      })
      .addCase(completeTodo.pending, (state, action) => {
        state.completingIds[action.meta.arg] = true;
      })
      .addCase(completeTodo.fulfilled, (state, action) => {
        delete state.completingIds[action.meta.arg];
        const index = state.items.findIndex(
          (todo) => todo.id === action.payload.id,
        );
        if (index !== -1) state.items[index] = action.payload;
      })
      .addCase(completeTodo.rejected, (state, action) => {
        delete state.completingIds[action.meta.arg];
      })
      .addCase(deleteTodo.pending, (state, action) => {
        state.deletingIds[action.meta.arg] = true;
      })
      .addCase(deleteTodo.fulfilled, (state, action) => {
        delete state.deletingIds[action.payload];
        state.items = state.items.filter(
          (todo) => todo.id !== action.payload,
        );
      })
      .addCase(deleteTodo.rejected, (state, action) => {
        delete state.deletingIds[action.meta.arg];
      })
      // English: Remove private data when the login session ends.
      // Roman Urdu: Login khatam ho to private todo data hata do.
      .addCase(loggedOut, () => initialState)
      .addCase(sessionExpired, () => initialState);
  },
});

export default todosSlice.reducer;
