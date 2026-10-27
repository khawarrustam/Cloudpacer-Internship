import { createSelector } from '@reduxjs/toolkit';
import {
  selectTaskFilter,
  selectTaskQuery,
  selectTaskSort,
} from '../taskView/taskViewSlice';

const PRIORITY_WEIGHT = { HIGH: 3, MEDIUM: 2, LOW: 1 };

export const selectAllTodos = (state) => state.todos.items;
export const selectTodosFetchStatus = (state) => state.todos.fetchStatus;
export const selectTodosError = (state) => state.todos.fetchError;
export const selectCreateStatus = (state) => state.todos.createStatus;
export const selectCompletingIds = (state) => state.todos.completingIds;
export const selectDeletingIds = (state) => state.todos.deletingIds;

export const selectTodoStats = createSelector(
  [selectAllTodos],
  (todos) => {
    const completed = todos.filter(
      (todo) => todo.is_completed,
    ).length;

    return {
      total: todos.length,
      completed,
      pending: todos.length - completed,
    };
  },
);

export const selectVisibleTodos = createSelector(
  [selectAllTodos, selectTaskFilter, selectTaskQuery, selectTaskSort],
  (todos, filter, query, sort) => {
    const normalizedQuery = query.trim().toLowerCase();

    return [...todos]
      .filter((todo) => {
        if (filter === 'active' && todo.is_completed) return false;
        if (filter === 'completed' && !todo.is_completed) return false;

        return !normalizedQuery
          || todo.title.toLowerCase().includes(normalizedQuery);
      })
      .sort((firstTodo, secondTodo) => {
        if (sort === 'newest') {
          return new Date(secondTodo.created_at)
            - new Date(firstTodo.created_at);
        }

        if (sort === 'oldest') {
          return new Date(firstTodo.created_at)
            - new Date(secondTodo.created_at);
        }

        if (firstTodo.is_completed !== secondTodo.is_completed) {
          return Number(firstTodo.is_completed)
            - Number(secondTodo.is_completed);
        }

        const priorityDifference = (
          PRIORITY_WEIGHT[String(secondTodo.priority).toUpperCase()] || 0
        ) - (
          PRIORITY_WEIGHT[String(firstTodo.priority).toUpperCase()] || 0
        );

        return priorityDifference
          || new Date(secondTodo.created_at)
          - new Date(firstTodo.created_at);
      });
  },
);
