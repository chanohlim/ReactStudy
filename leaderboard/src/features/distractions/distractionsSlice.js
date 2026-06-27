import { createSlice, nanoid } from '@reduxjs/toolkit';

const initialState = {
  entries: [
    { id: 'seed-1', name: '김대리', type: '유튜브 쇼츠', minutes: 132, createdAt: '2026-06-27T09:00:00.000Z' },
    { id: 'seed-2', name: '박사원', type: '간식 원정대', minutes: 96, createdAt: '2026-06-27T09:05:00.000Z' },
    { id: 'seed-3', name: '이주임', type: '메신저 수다', minutes: 74, createdAt: '2026-06-27T09:10:00.000Z' },
    { id: 'seed-4', name: '최인턴', type: '창밖 멍때리기', minutes: 51, createdAt: '2026-06-27T09:15:00.000Z' },
  ],
};

const distractionsSlice = createSlice({
  name: 'distractions',
  initialState,
  reducers: {
    addDistraction: {
      reducer(state, action) {
        state.entries.push(action.payload);
      },
      prepare({ name, type, minutes }) {
        return {
          payload: {
            id: nanoid(),
            name,
            type,
            minutes: Number(minutes),
            createdAt: new Date().toISOString(),
          },
        };
      },
    },
    removeDistraction(state, action) {
      state.entries = state.entries.filter((entry) => entry.id !== action.payload);
    },
    clearDistractions(state) {
      state.entries = [];
    },
  },
});

export const { addDistraction, removeDistraction, clearDistractions } = distractionsSlice.actions;

export const selectEntries = (state) => state.distractions.entries;

export const selectRankedEntries = (state) => {
  return [...state.distractions.entries].sort((a, b) => {
    if (b.minutes !== a.minutes) {
      return b.minutes - a.minutes;
    }
    return new Date(a.createdAt) - new Date(b.createdAt);
  });
};

export const selectDistractionStats = (state) => {
  const entries = state.distractions.entries;
  const totalMinutes = entries.reduce((total, entry) => total + entry.minutes, 0);
  const topEntry = selectRankedEntries(state)[0];
  const averageMinutes = entries.length ? Math.round(totalMinutes / entries.length) : 0;

  return {
    totalMinutes,
    averageMinutes,
    entryCount: entries.length,
    topEntry,
  };
};

export default distractionsSlice.reducer;
