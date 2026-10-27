import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  // English: These values only control how the todo list looks.
  // Roman Urdu: Yeh values sirf todo list ka view control karti hain.
  filter: 'all',
  query: '',
  sort: 'smart',
};

const taskViewSlice = createSlice({
  name: 'taskView',
  initialState,
  reducers: {
    // English: Each reducer changes one simple view setting.
    // Roman Urdu: Har reducer aik simple view setting change karta hai.
    filterChanged(state, action) {
      state.filter = action.payload;
    },
    queryChanged(state, action) {
      state.query = action.payload;
    },
    sortChanged(state, action) {
      state.sort = action.payload;
    },
  },
});

export const {
  filterChanged,
  queryChanged,
  sortChanged,
} = taskViewSlice.actions;

export const selectTaskFilter = (state) => state.taskView.filter;
export const selectTaskQuery = (state) => state.taskView.query;
export const selectTaskSort = (state) => state.taskView.sort;

export default taskViewSlice.reducer;
