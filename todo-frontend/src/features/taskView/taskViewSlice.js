import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  filter: 'all',
  query: '',
  sort: 'smart',
};

const taskViewSlice = createSlice({
  name: 'taskView',
  initialState,
  reducers: {
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
