import { configureStore } from '@reduxjs/toolkit';
import distractionsReducer from './features/distractions/distractionsSlice';

export const store = configureStore({
  reducer: {
    distractions: distractionsReducer,
  },
});
