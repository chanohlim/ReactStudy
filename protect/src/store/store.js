import { configureStore } from '@reduxjs/toolkit';
import workDefenseReducer from '../features/workDefenseSlice';

export const store = configureStore({
  reducer: {
    workDefense: workDefenseReducer,
  },
});
