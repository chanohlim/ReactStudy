import { useReducer, useState } from 'react';

// Dispatch(Action) ====> Reducer(State, Action) ==> State 업데이트

const bankReducer = (bankState, bankAction) => { // Reducer 함수 정의
  
  switch(bankAction.mode){
    case 'deposit':
      return bankState + bankAction.amount;
    case 'withdraw':
      return bankState - bankAction.amount;
    default:
      return bankState;

  }
}

const UseReducerExam = () => {
  const [inputMoney, setInputMoney] = useState(0);
  const [balance, bankDispatch] = useReducer(bankReducer, 0);
  const [log, setLog] = useState('초기 상태');

  return(<>
    <h2>UseReducer 사용하기</h2>
    <p>잔고 : {balance}원</p>
      <input
      type = "number"
      value = {inputMoney}
      step = {1000}
      onChange={(e)=>{
        setInputMoney(parseInt(e.target.value));
      }}
      ></input>
      <button
      type='button'
      onClick={()=>{
        bankDispatch({mode:'deposit', amount:inputMoney});
        setLog(`리듀서 호출: deposit +${inputMoney} = ${balance + inputMoney}`);
      }}
      >입금</button>
      <button
      type='button'
      onClick={()=>{
        bankDispatch({mode:'withdraw', amount:inputMoney});
        setLog(`리듀서 호출: withdraw -${inputMoney} = ${balance - inputMoney}`);
      }}
      >출금</button>
    <p>{log}</p>
  </>);
}

export default UseReducerExam;