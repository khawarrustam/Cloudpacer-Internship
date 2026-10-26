import { createSelector } from '@reduxjs/toolkit';
import {
    selectTaskFilter,
    selectTaskQuery,
    selectTaskSort,
} from '../taskView/taskViewSlice';

export const selectAllTodos = (state) => state.todos.items;
export const selectTodosFetchStatus = (state) => state.todos.fetchStatus;
export const selectTodosError = (state) => state.todos.fetchError;
export const selectCreateStatus = (state) => state.todos.createStatus;
export const selectCompletingIds = (state) => state.todos.completingIds;
export const selectDeletingIds = (state) => state.todos.deletingIds;

export const selectTodoStats = createSelector([selectAllTodos], (todos) => {
    const completed = todos.filter((todo) => todo.is_completed).length;
    return {
        total: todos.length,
        completed,
        pending: todos.length - completed,
    };
});

export const selectVisibleTodos = createSelector(
    [selectAllTodos, selectTaskFilter, selectTaskQuery, selectTaskSort],
    (todos, filter, query, sort) => {
        const priorityWeight = { HIGH: 3, MEDIUM: 2, LOW: 1 };
        const normalizedQuery = query.trim().toLowerCase();

        return todos
            .filter((todo) => {
                if (filter === 'active' && todo.is_completed) return false;
                if (filter === 'completed' && !todo.is_completed) return false;
                return !normalizedQuery || todo.title.toLowerCase().includes(normalizedQuery);
            })
            .sort((a, b) => {
                if (sort === 'newest') {
                    return new Date(b.created_at) - new Date(a.created_at);
                }
                if (sort === 'oldest') {
                    return new Date(a.created_at) - new Date(b.created_at);
                }
                if (a.is_completed !== b.is_completed) {
                    return Number(a.is_completed) - Number(b.is_completed);
                }
                const priorityDifference =
                    (priorityWeight[String(b.priority).toUpperCase()] || 0) -
                    (priorityWeight[String(a.priority).toUpperCase()] || 0);
                return priorityDifference || new Date(b.created_at) - new Date(a.created_at);
            });
    },
);