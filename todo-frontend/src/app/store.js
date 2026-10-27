import { configureStore } from '@reduxjs/toolkit';
import authReducer from '../features/auth/authSlice';
import taskViewReducer from '../features/taskView/taskViewSlice';
import todosReducer from '../features/todos/todosSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    todos: todosReducer,
    taskView: taskViewReducer,
  },
});
