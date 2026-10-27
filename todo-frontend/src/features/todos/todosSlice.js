import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { getTodoErrorMessage } from '../../api/errors';
import { todoApi } from '../../api/todoApi';
import { loggedOut, sessionExpired } from '../auth/authSlice';

// English: Fetch thunk gets the signed-in user's todos from the backend.
// Roman Urdu: Fetch thunk backend se signed-in user ke todos laata hai.
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

// English: Create thunk sends form data and returns the saved todo.
// Roman Urdu: Create thunk form data bhej kar saved todo wapas laata hai.
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

// English: Complete thunk sends one id and returns the updated todo.
// Roman Urdu: Complete thunk aik id bhej kar updated todo wapas laata hai.
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

// English: Delete thunk sends one id and returns it after success.
// Roman Urdu: Delete thunk aik id bhejta aur success ke baad wohi id return karta hai.
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
  // English: Backend todo records live in this Redux array.
  // Roman Urdu: Backend ke todo records is Redux array mein rehte hain.
  items: [],

  // English: Separate statuses keep each button/loading state simple.
  // Roman Urdu: Alag statuses har button aur loading state ko simple rakhte hain.
  fetchStatus: 'idle',
  createStatus: 'idle',
  completingIds: {},
  deletingIds: {},
  fetchError: null,
};

// English: Replace one old todo with the updated todo from the backend.
// Roman Urdu: Backend se aaye updated todo ko puranay todo ki jagah rakho.
function replaceTodo(items, updatedTodo) {
  const todoIndex = items.findIndex((todo) => todo.id === updatedTodo.id);

  if (todoIndex !== -1) {
    items[todoIndex] = updatedTodo;
  }
}

const todosSlice = createSlice({
  name: 'todos',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    // English: Fulfilled reducers are the only place that update todo records.
    // Roman Urdu: Todo records sirf fulfilled reducers mein update hotay hain.
    builder
      // FETCH: loading starts -> API succeeds/fails -> Redux saves the result.
      // Roman Urdu: FETCH mein loading, success ya error Redux mein save hota hai.
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
      // CREATE: disable the button while saving, then add the saved todo.
      // Roman Urdu: Save hotay waqt button disable karo, phir saved todo add karo.
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
      // COMPLETE: only the clicked todo shows a loading state.
      // Roman Urdu: Sirf clicked todo par loading state show hoti hai.
      .addCase(completeTodo.pending, (state, action) => {
        state.completingIds[action.meta.arg] = true;
      })
      .addCase(completeTodo.fulfilled, (state, action) => {
        delete state.completingIds[action.meta.arg];
        replaceTodo(state.items, action.payload);
      })
      .addCase(completeTodo.rejected, (state, action) => {
        delete state.completingIds[action.meta.arg];
      })
      // DELETE: only the clicked todo shows loading, then Redux removes it.
      // Roman Urdu: Clicked todo loading dikhata hai, phir Redux usay hata deta hai.
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
