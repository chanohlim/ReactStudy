import { createSlice } from '@reduxjs/toolkit';
import { analyzeWorkDefense, DEFAULT_RESULT } from '../utils/timeAnalysis';

const initialForm = {
  title: '',
  description: '',
  requestTime: '17:30',
  finishTime: '18:00',
  estimatedMinutes: '60',
  urgency: '보통',
  requiredToday: false,
};

const initialState = {
  form: initialForm,
  result: DEFAULT_RESULT,
  history: [],
};

const workDefenseSlice = createSlice({
  name: 'workDefense',
  initialState,
  reducers: {
    updateField: (state, action) => {
      const { field, value } = action.payload;
      if (field in state.form) {
        state.form[field] = value;
      }
    },
    analyzeTask: (state) => {
      state.result = analyzeWorkDefense(state.form);
    },
    resetForm: (state) => {
      state.form = initialForm;
      state.result = DEFAULT_RESULT;
    },
    saveAnalysis: (state) => {
      if (state.result.error) return;

      state.history.unshift({
        id: crypto.randomUUID(),
        createdAt: new Date().toISOString(),
        form: { ...state.form },
        result: { ...state.result },
      });
      state.history = state.history.slice(0, 6);
    },
    deleteAnalysis: (state, action) => {
      state.history = state.history.filter((item) => item.id !== action.payload);
    },
  },
});

export const { updateField, analyzeTask, resetForm, saveAnalysis, deleteAnalysis } = workDefenseSlice.actions;
export default workDefenseSlice.reducer;
