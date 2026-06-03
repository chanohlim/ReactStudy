import { useActionState, useRef, useEffect } from 'react';

async function authLogin(prevState, formData) {
  const userid = formData.get('userid');
  const userpw = formData.get('userpw');

  await new Promise(resolve => {
    setTimeout(resolve, 1000);
  });

  if (userid === 'chanlim' && userpw === 'Chanoh8893') {
    return '로그인 성공!';
  }
  else {
    return '로그인 실패';
  }
}

const UseActionStateExam = () => {
  const [message, formAction, isPending] = useActionState(authLogin, null);
  const inputRef = useRef();

  useEffect(() => {
    inputRef.current.focus();
  }, [])


  return (<>
    <h2>useActionState 사용하기</h2>
    <form action={formAction}>
      아이디: <input type='text' name='userid' ref={inputRef}></input> <br />
      비번: <input type='text' name='userpw'></input> <br />
      <button type='submit'>로그인</button>
      {isPending ? 'Loading...' : message}
    </form>
  </>);
}

export default UseActionStateExam;