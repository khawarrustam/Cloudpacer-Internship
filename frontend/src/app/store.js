import { configureStore } from '@reduxjs/toolkit';
import authReducer from '../features/auth/authSlice';
import taskViewReducer from '../features/taskView/taskViewSlice';
import todosReducer from '../features/todos/todosSlice';

// English: The store joins the three small Redux state sections.
// Roman Urdu: Store teen chhoti Redux state sections ko jorta hai.
export const store = configureStore({
  reducer: {
    auth: authReducer,
    todos: todosReducer,
    taskView: taskViewReducer,
  },
});
