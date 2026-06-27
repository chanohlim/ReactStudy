/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, useSyncExternalStore } from 'react';

const StoreContext = createContext(null);

export function Provider({ store, children }) {
  return <StoreContext.Provider value={store}>{children}</StoreContext.Provider>;
}

export function useDispatch() {
  const store = useContext(StoreContext);

  if (!store) {
    throw new Error('useDispatch must be used within a Provider.');
  }

  return store.dispatch;
}

export function useSelector(selector) {
  const store = useContext(StoreContext);

  if (!store) {
    throw new Error('useSelector must be used within a Provider.');
  }

  return useSyncExternalStore(store.subscribe, () => selector(store.getState()), () => selector(store.getState()));
}
