import { useState } from 'react';

function WriteForm(props){
  return(<>
    <form onSubmit={(e)=>{
      console.log("이벤트객체e",e);
      e.preventDefault();
      let gubun = e.target.gubun.value;
      let title = e.target.title.value;
      props.writeAction(gubun, title);
    }}>
        <select name="gubun">
            <option value="front">프론트엔드</option>
            <option value="back">백엔드</option>
        </select>
        <input type="text" name="title" />
        <input type="submit" value="추가" />
    </form>
  </>)
}

const TopComp = ({MyData}) => {
  return(<>
    <ol>
      <li>프론트엔드</li>
      <ul>
        {MyData.front.map((item, i) => <li key={i}>{item}</li>)}
      </ul>
      <li>백엔드</li>
      <ul>
        {MyData.back.map((item, i) => <li key={i}>{item}</li>)}
      </ul>
    </ol>
  </>)
}

function App(){
  const [MyData, setMyData] = useState({
    front: ['HTML5', 'CSS3', 'Javascript', 'jQuery'],
    back: ['Java', 'Oracle', 'JSP', 'SpringBoot'],
  });
  const [message, setMessage] = useState("폼값 입력 안됨");
  const addData = (type, msg) => {
    setMyData({
      ...MyData, 
      [type]: [...MyData[type], msg]
    });
  }
  return(<>
    <h2>React-Shallow Comparison</h2>
    <TopComp MyData={MyData}></TopComp>
    <WriteForm writeAction = {(gu, ti) => {
      if (gu !== '' && ti !== ''){
        addData(gu, ti);
        setMessage(`폼값 업데이트 됨: ${gu}, ${ti}`);
      }
    }}></WriteForm>
    <pre>{message}</pre>
    
  </>)
}

export default App;

