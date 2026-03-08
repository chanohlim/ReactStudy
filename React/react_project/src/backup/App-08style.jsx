import jqueryLogo from './assets/jQuery.png'
import reactLogo from './assets/react.svg'

function App(){
  const myStyle = {
    color: "white",
    backgroundColor: "DodgerBlue",
    padding: "10px",
    fontFamily: "Verdana"
  };
  const iWidth = {maxWidth: '300px'};
  return(
  <>
    <h2>React-Style</h2>
      <ol>
          <li style={{color : "red"}}>프론트엔드</li>
          <ul>
              <li><img src="/img/html_css_js.png" style={iWidth}/></li>
              <li><img src={jqueryLogo} style={iWidth}/></li>
              <li><h2 style={{color : "lightblue",  backgroundColor : "black"}}>React</h2></li>
              <li><img src={reactLogo}/></li>
          </ul>
          <li className='backEnd'>백엔드</li>
          <ul>
              <li id='backEndSub'>Java</li>
              <li class='warnings'>Oracle</li>
              <li style={myStyle}>JSP</li>
              <li>Spring Boot</li>
          </ul>
      </ol>
  </>
  )
}

export default App
