import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  completeTodo,
  createTodo,
  deleteTodo,
  fetchTodos,
} from '../features/todos/todosSlice';
import {
  selectAllTodos,
  selectCompletingIds,
  selectCreateStatus,
  selectDeletingIds,
  selectTodoStats,
  selectTodosError,
  selectTodosFetchStatus,
  selectVisibleTodos,
} from '../features/todos/todosSelectors';
import {
  filterChanged,
  queryChanged,
  selectTaskFilter,
  selectTaskQuery,
  selectTaskSort,
  sortChanged,
} from '../features/taskView/taskViewSlice';

// English: Redux owns todo data; this hook gives the UI simple actions and values.
// Roman Urdu: Todo data Redux mein hai; yeh hook UI ko asaan values aur actions deta hai.
export function useTodos() {
  const dispatch = useDispatch();
  const todos = useSelector(selectAllTodos);
  const visibleTodos = useSelector(selectVisibleTodos);
  const stats = useSelector(selectTodoStats);
  const fetchStatus = useSelector(selectTodosFetchStatus);
  const createStatus = useSelector(selectCreateStatus);
  const completingIds = useSelector(selectCompletingIds);
  const deletingIds = useSelector(selectDeletingIds);
  const error = useSelector(selectTodosError);
  const filter = useSelector(selectTaskFilter);
  const query = useSelector(selectTaskQuery);
  const sort = useSelector(selectTaskSort);

  // English: Load once when the dashboard opens.
  // Roman Urdu: Dashboard khulte hi todos aik dafa load karo.
  useEffect(() => {
    if (fetchStatus === 'idle') {
      dispatch(fetchTodos());
    }
  }, [dispatch, fetchStatus]);

  return {
    todos,
    visibleTodos,
    stats,
    error,
    filter,
    query,
    sort,
    loading: fetchStatus === 'loading',
    creating: createStatus === 'loading',
    completingIds,
    deletingIds,
    refresh: () => dispatch(fetchTodos()),
    addTodo: (todo) => dispatch(createTodo(todo)).unwrap(),
    finishTodo: (id) => dispatch(completeTodo(id)).unwrap(),
    removeTodo: (id) => dispatch(deleteTodo(id)).unwrap(),
    setFilter: (value) => dispatch(filterChanged(value)),
    setQuery: (value) => dispatch(queryChanged(value)),
    setSort: (value) => dispatch(sortChanged(value)),
  };
}
