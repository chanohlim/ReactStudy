export function nanoid() {
  return Math.random().toString(36).slice(2, 10) + Date.now().toString(36);
}

function cloneState(state) {
  if (typeof structuredClone === 'function') {
    return structuredClone(state);
  }

  return JSON.parse(JSON.stringify(state));
}

export function createSlice({ name, initialState, reducers }) {
  const actionCreators = {};
  const caseReducers = {};

  Object.entries(reducers).forEach(([reducerName, reducerDefinition]) => {
    const type = `${name}/${reducerName}`;
    const reducer = typeof reducerDefinition === 'function' ? reducerDefinition : reducerDefinition.reducer;
    const prepare = typeof reducerDefinition === 'function' ? undefined : reducerDefinition.prepare;

    caseReducers[type] = reducer;
    actionCreators[reducerName] = (...args) => {
      if (prepare) {
        return { type, ...prepare(...args) };
      }

      return { type, payload: args[0] };
    };
  });

  return {
    actions: actionCreators,
    reducer(state = initialState, action) {
      const reducer = caseReducers[action.type];

      if (!reducer) {
        return state;
      }

      const nextState = cloneState(state);
      reducer(nextState, action);
      return nextState;
    },
  };
}

export function configureStore({ reducer }) {
  let state = Object.fromEntries(
    Object.entries(reducer).map(([key, reducerFunction]) => [key, reducerFunction(undefined, { type: '@@INIT' })]),
  );
  const listeners = new Set();

  return {
    dispatch(action) {
      state = Object.fromEntries(
        Object.entries(reducer).map(([key, reducerFunction]) => [key, reducerFunction(state[key], action)]),
      );
      listeners.forEach((listener) => listener());
      return action;
    },
    getState() {
      return state;
    },
    subscribe(listener) {
      listeners.add(listener);
      return () => listeners.delete(listener);
    },
  };
}
