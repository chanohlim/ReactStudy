import { create } from 'zustand';

const useCounterStore = create((set, get) => ({
  count: 0,

  increment: () => {
    const current = get().count;
    if (current >= 10) {
      alert('최댓값은 10입니다.');
      return;
    }
    set({count : current + 1});
  },

  decrement: () => {
    const current = get().count;
    if (current <= 0) {
      alert('최솟값은 0입니다.');
      return;
    }
    set({count : current - 1});
  },

  reset: () => set({count : 0})
}));

export default useCounterStore;