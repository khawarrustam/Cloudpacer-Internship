import { configureStore } from '@reduxjs/toolkit';
import authReducer from '../features/auth/authSlice';
import todosReducer from '../features/todos/todosSlice';
import taskViewReducer from '../features/taskView/taskViewSlice';

export const store = configureStore({
    reducer: {
        auth: authReducer,
        todos: todosReducer,
        taskView: taskViewReducer,
    },
});