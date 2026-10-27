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

  // English: Selectors read values from Redux without changing them.
  // Roman Urdu: Selectors Redux values ko bina change kiye read karte hain.
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

  // English: Each function sends one clear action to Redux.
  // Roman Urdu: Har function Redux ko aik clear action bhejta hai.
  const refresh = () => dispatch(fetchTodos());
  const addTodo = (todo) => dispatch(createTodo(todo)).unwrap();
  const finishTodo = (id) => dispatch(completeTodo(id)).unwrap();
  const removeTodo = (id) => dispatch(deleteTodo(id)).unwrap();

  // English: These actions change only the list view, not backend data.
  // Roman Urdu: Yeh actions sirf list view change karte hain, backend data nahi.
  const setFilter = (value) => dispatch(filterChanged(value));
  const setQuery = (value) => dispatch(queryChanged(value));
  const setSort = (value) => dispatch(sortChanged(value));

  // English: Components receive simple values and functions from this object.
  // Roman Urdu: Components ko is object se simple values aur functions milte hain.
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
    refresh,
    addTodo,
    finishTodo,
    removeTodo,
    setFilter,
    setQuery,
    setSort,
  };
}
