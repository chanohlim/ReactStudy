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
        const { name, type, minutes, createdAt } = action.payload;
        const existingPerson = state.people.find((person) => normalizeName(person.name) === normalizeName(name));

        if (!state.types.some((savedType) => normalizeType(savedType) === normalizeType(type))) {
          state.types.push(type);
        }

        if (!existingPerson) {
          state.people.push({
            id: nanoid(),
            name,
            createdAt,
            distractions: [{ id: nanoid(), type, minutes }],
          });
          return;
        }

        const existingDistraction = existingPerson.distractions.find((distraction) => {
          return normalizeType(distraction.type) === normalizeType(type);
        });

        if (existingDistraction) {
          existingDistraction.minutes += minutes;
          return;
        }

        existingPerson.distractions.push({ id: nanoid(), type, minutes });
      },
      prepare({ name, type, minutes }) {
        return {
          payload: {
            name: name.trim(),
            type: type.trim(),
            minutes: Number(minutes),
            createdAt: new Date().toISOString(),
          },
        };
      },
    },
    addDistractionType(state, action) {
      const type = action.payload.trim();

      if (!type) {
        return;
      }

      if (!state.types.some((savedType) => normalizeType(savedType) === normalizeType(type))) {
        state.types.push(type);
      }
    },
    removePerson(state, action) {
      state.people = state.people.filter((person) => person.id !== action.payload);
    },
    removeDistraction(state, action) {
      const { personId, distractionId } = action.payload;
      const person = state.people.find((currentPerson) => currentPerson.id === personId);

      if (!person) {
        return;
      }

      person.distractions = person.distractions.filter((distraction) => distraction.id !== distractionId);

      if (person.distractions.length === 0) {
        state.people = state.people.filter((currentPerson) => currentPerson.id !== personId);
      }
    },
    clearDistractions(state) {
      state.people = [];
    },
  },
});

export const {
  addDistraction,
  addDistractionType,
  clearDistractions,
  removeDistraction,
  removePerson,
} = distractionsSlice.actions;

export const selectDistractionTypes = (state) => state.distractions.types;
export const selectPeople = (state) => state.distractions.people;

export const selectRankedPeople = (state) => {
  return [...state.distractions.people]
    .map((person) => ({
      ...person,
      totalMinutes: getTotalMinutes(person),
      topDistraction: [...person.distractions].sort((a, b) => b.minutes - a.minutes)[0],
    }))
    .sort((a, b) => {
      if (b.totalMinutes !== a.totalMinutes) {
        return b.totalMinutes - a.totalMinutes;
      }
      return new Date(a.createdAt) - new Date(b.createdAt);
    });
};

export const selectDistractionStats = (state) => {
  const rankedPeople = selectRankedPeople(state);
  const totalMinutes = rankedPeople.reduce((total, person) => total + person.totalMinutes, 0);
  const distractionCount = rankedPeople.reduce((total, person) => total + person.distractions.length, 0);
  const averageMinutes = rankedPeople.length ? Math.round(totalMinutes / rankedPeople.length) : 0;
  const typeCounts = rankedPeople.reduce((counts, person) => {
    person.distractions.forEach((distraction) => {
      counts[distraction.type] = (counts[distraction.type] || 0) + distraction.minutes;
    });
    return counts;
  }, {});
  const topType = Object.entries(typeCounts).sort((a, b) => b[1] - a[1])[0]?.[0] || '집계 중';

  return {
    totalMinutes,
    averageMinutes,
    personCount: rankedPeople.length,
    distractionCount,
    topPerson: rankedPeople[0],
    topType,
  };
};

export default distractionsSlice.reducer;
