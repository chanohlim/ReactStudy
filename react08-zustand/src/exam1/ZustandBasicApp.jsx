import useCounterStore from "./useCounterStore";

function ZustandBasicApp() {
  const { count, increment, decrement, reset } = useCounterStore();

  return(<>
    <h2>Zustand 기본 사용법</h2>
    <h3>현재 값: {count}</h3>
    <button onClick={increment}>+1</button>
    <button onClick={decrement}>-1</button>
    <button onClick={reset}>초기화</button>
  </>)
}


export default ZustandBasicApp;