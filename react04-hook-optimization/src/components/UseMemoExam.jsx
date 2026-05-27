import { useState, useEffect } from 'react';

const isPrime = (num) => {
  for(let exCost=1; exCost<123456789; exCost++){
    //
  }
  if (num <= 1) return false;
  for(let i = 2; i <= Math.sqrt(num); i++){
    if (num % i === 0) return false;
  }
  return true;
};

const useMemoExam = () => {
  const [number, setNumber] = useState(0);
  const [text, setText] = useState('');
  const [log, setLog] = useState('대기중...');
  const [checkPrime, setCheckPrime] = useState(false);



  useEffect(()=>{

    setLog('소수 판단중...');

    const timer = setTimeout(()=>{
      const result = isPrime(number);

      setCheckPrime(result);
      setLog('소수 판단 완료!');

    }, 100);

    return() => clearTimeout(timer)
  }, [number]);

  return(<>
    <h2>useMemo 사용하기</h2>

    <input
    type="number"
    value={number}
    placeholder="소수 판단할 숫자 입력"
    onChange={(e) => {
      setNumber(parseInt(e.target.value))
    }}>
    </input>

    <p>정수 {number}는 {checkPrime ? '소수 O' : '소수 X'}</p>

    <input
    type="text"
    value={text}
    placeholder="이름 입력(소수 판단과 무관)"
    onChange={(e) => setText(e.target.value)} 
    />
    <p>입력한 이름: {text}</p>
    <p>{log}</p>
  </>);
};

export default useMemoExam;