import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { todoApi } from '../../api/todoApi';
import { loggedOut, sessionExpired } from '../auth/authSlice';

function errorMessage(error, fallback) {
    if (error.response?.status === 401) {
        return 'Session expired. Please log in again.';
    }
    if (error.response?.status === 403) {
        return 'You do not have permission to access these tasks.';
    }
    return error.response?.data?.detail || fallback;
}

export const fetchTodos = createAsyncThunk(
    'todos/fetchTodos',
    async (_, { rejectWithValue }) => {
        try {
            return await todoApi.getAll();
        } catch (error) {
            return rejectWithValue(
                errorMessage(error, 'Unable to connect to the server. Is the backend running?'),
            );
        }
    },
    {
        condition: (_, { getState }) => {
            return getState().todos.fetchStatus !== 'loading';
        },
    },
);

export const createTodo = createAsyncThunk(
    'todos/createTodo',
    async ({ title, priority }, { rejectWithValue }) => {
        try {
            return await todoApi.create({ title, priority });
        } catch (error) {
            return rejectWithValue(errorMessage(error, 'Failed to add todo'));
        }
    },
);

export const completeTodo = createAsyncThunk(
    'todos/completeTodo',
    async (id, { rejectWithValue }) => {
        try {
            return await todoApi.complete(id);
        } catch (error) {
            return rejectWithValue(errorMessage(error, 'Failed to complete todo'));
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
            return rejectWithValue(errorMessage(error, 'Failed to delete todo'));
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
    mutationError: null,
};

const todosSlice = createSlice({
    name: 'todos',
    initialState,
    reducers: {
        clearTodosError(state) {
            state.fetchError = null;
            state.mutationError = null;
        },
        resetTodos() {
            return initialState;
        },
    },
    extraReducers: (builder) => {
        builder
            // Fetch
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

            // Create
            .addCase(createTodo.pending, (state) => {
                state.createStatus = 'loading';
                state.mutationError = null;
            })
            .addCase(createTodo.fulfilled, (state, action) => {
                state.createStatus = 'succeeded';
                state.items.push(action.payload);
            })
            .addCase(createTodo.rejected, (state, action) => {
                state.createStatus = 'failed';
                state.mutationError = action.payload || action.error.message;
            })

            // Complete
            .addCase(completeTodo.pending, (state, action) => {
                state.completingIds[action.meta.arg] = true;
                state.mutationError = null;
            })
            .addCase(completeTodo.fulfilled, (state, action) => {
                delete state.completingIds[action.meta.arg];
                const index = state.items.findIndex((todo) => todo.id === action.payload.id);
                if (index !== -1) state.items[index] = action.payload;
            })
            .addCase(completeTodo.rejected, (state, action) => {
                delete state.completingIds[action.meta.arg];
                state.mutationError = action.payload || action.error.message;
            })

            // Delete
            .addCase(deleteTodo.pending, (state, action) => {
                state.deletingIds[action.meta.arg] = true;
                state.mutationError = null;
            })
            .addCase(deleteTodo.fulfilled, (state, action) => {
                delete state.deletingIds[action.payload];
                state.items = state.items.filter((todo) => todo.id !== action.payload);
            })
            .addCase(deleteTodo.rejected, (state, action) => {
                delete state.deletingIds[action.meta.arg];
                state.mutationError = action.payload || action.error.message;
            })

            // Auth ends: private data must disappear immediately
            .addCase(loggedOut, () => initialState)
            .addCase(sessionExpired, () => initialState);
    },
});

export const { clearTodosError, resetTodos } = todosSlice.actions;
export default todosSlice.reducer;