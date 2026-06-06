import {NavLink} from 'react-router-dom';

const TopNavi = () =>{
  return(
    <nav>
      <NavLink to='/ReduxBasicApp'>기본사용법</NavLink>&nbsp;
      <NavLink to='/TodoApp'>할 일 관리</NavLink>&nbsp;
    </nav>
  );
}

export default TopNavi;