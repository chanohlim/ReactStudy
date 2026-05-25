import { useId, useEffect } from "react";

const InputField = ({ label, name, autoFocus = false }) => {
  const id = useId();

  useEffect(() => {
    if (autoFocus) {
      document.getElementById(id).focus();
    }
  }, []);

  return (<>
    <label htmlFor={id}>{label}</label>
    <input
    type="text"
    id={id}
    name={name}></input>
  </>);
};

const MyForm = () => {
  const commonId = useId();

  return (
    <div>
      <InputField
      label="아이디"
      name="id"
      autoFocus
      ></InputField><br />
      <InputField
      label="이름"
      name="name"
      ></InputField><br />
      성별
      <input
      type="radio"
      id={`${commonId}-gender1`}
      name="gender"
      ></input>
      <label htmlFor={`${commonId}-gender1`}>남자</label>
      <input
      type="radio"
      id={`${commonId}-gender2`}
      name="gender"
      ></input>
      <label htmlFor={`${commonId}-gender2`}>여자</label>
    </div>
  );
};

const UseIdExam = () => {
  return(<>
    <h2>useId() 사용하기</h2>
    <MyForm />
  </>);
};

export default UseIdExam;