import { createSelector } from '@reduxjs/toolkit';
import {
  selectTaskFilter,
  selectTaskQuery,
  selectTaskSort,
} from '../taskView/taskViewSlice';

const PRIORITY_WEIGHT = { HIGH: 3, MEDIUM: 2, LOW: 1 };

// English: Return true when a todo belongs to the selected tab.
// Roman Urdu: Agar todo selected tab mein aata ho to true return karo.
function matchesSelectedFilter(todo, filter) {
  if (filter === 'active') {
    return !todo.is_completed;
  }

  if (filter === 'completed') {
    return todo.is_completed;
  }

  return true;
}

// English: An empty search shows every todo.
// Roman Urdu: Search khaali ho to har todo show karo.
function matchesSearch(todo, searchText) {
  if (!searchText) {
    return true;
  }

  return todo.title.toLowerCase().includes(searchText);
}

function compareDates(firstDate, secondDate) {
  return new Date(firstDate) - new Date(secondDate);
}

// English: Keep all sorting rules in one small function.
// Roman Urdu: Saare sorting rules aik chotay function mein rakho.
function compareTodos(firstTodo, secondTodo, sort) {
  if (sort === 'newest') {
    return compareDates(secondTodo.created_at, firstTodo.created_at);
  }

  if (sort === 'oldest') {
    return compareDates(firstTodo.created_at, secondTodo.created_at);
  }

  // Smart order: open tasks first, then high priority, then newest.
  // Roman Urdu: Smart order mein open, phir high priority, phir newest aata hai.
  if (firstTodo.is_completed !== secondTodo.is_completed) {
    return Number(firstTodo.is_completed) - Number(secondTodo.is_completed);
  }

  const firstPriority = PRIORITY_WEIGHT[
    String(firstTodo.priority).toUpperCase()
  ] || 0;
  const secondPriority = PRIORITY_WEIGHT[
    String(secondTodo.priority).toUpperCase()
  ] || 0;
  const priorityDifference = secondPriority - firstPriority;

  if (priorityDifference !== 0) {
    return priorityDifference;
  }

  return compareDates(secondTodo.created_at, firstTodo.created_at);
}

// English: Small selectors read one value from the Redux store.
// Roman Urdu: Small selectors Redux store se aik value read karte hain.
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
    // English: This selector derives the visible list; it does not change Redux data.
    // Roman Urdu: Yeh selector visible list banata hai; Redux data change nahi karta.
    const searchText = query.trim().toLowerCase();

    return [...todos]
      .filter((todo) => matchesSelectedFilter(todo, filter))
      .filter((todo) => matchesSearch(todo, searchText))
      .sort((firstTodo, secondTodo) => (
        compareTodos(firstTodo, secondTodo, sort)
      ));
  },
);
