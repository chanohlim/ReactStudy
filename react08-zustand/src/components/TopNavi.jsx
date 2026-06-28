import { NavLink } from "react-router-dom";

const TopNavi = () => {
  return(
    <nav>
      <NavLink to="/ZustandBasicApp">기본 사용법</NavLink>&nbsp;
      <NavLink to="/AttendanceApp">출결 관리</NavLink>&nbsp;
    </nav>
  );
}

export default TopNavi;