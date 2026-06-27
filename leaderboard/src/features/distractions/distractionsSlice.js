import { createSlice, nanoid } from '@reduxjs/toolkit';

const initialState = {
  types: [
    '유튜브 쇼츠',
    'SNS 탐험',
    '메신저 수다',
    '커피 산책',
    '간식 원정대',
    '창밖 멍때리기',
    '회의 중 딴생각',
  ],
  people: [
    {
      id: 'person-1',
      name: '김대리',
      createdAt: '2026-06-27T09:00:00.000Z',
      distractions: [
        { id: 'seed-1', type: '유튜브 쇼츠', minutes: 92 },
        { id: 'seed-2', type: '커피 산책', minutes: 40 },
      ],
    },
    {
      id: 'person-2',
      name: '박사원',
      createdAt: '2026-06-27T09:05:00.000Z',
      distractions: [
        { id: 'seed-3', type: '간식 원정대', minutes: 96 },
      ],
    },
    {
      id: 'person-3',
      name: '이주임',
      createdAt: '2026-06-27T09:10:00.000Z',
      distractions: [
        { id: 'seed-4', type: '메신저 수다', minutes: 74 },
      ],
    },
    {
      id: 'person-4',
      name: '최인턴',
      createdAt: '2026-06-27T09:15:00.000Z',
      distractions: [
        { id: 'seed-5', type: '창밖 멍때리기', minutes: 51 },
      ],
    },
  ],
};

const normalizeName = (name) => name.trim().toLocaleLowerCase('ko-KR');
const normalizeType = (type) => type.trim().toLocaleLowerCase('ko-KR');

const getTotalMinutes = (person) => {
  return person.distractions.reduce((total, distraction) => total + distraction.minutes, 0);
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
