import { configureStore } from './lib/reduxToolkit.js';
import distractionsReducer from './features/distractions/distractionsSlice';

export const store = configureStore({
  reducer: {
    distractions: distractionsReducer,
  },
});
