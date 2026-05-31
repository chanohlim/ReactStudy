import {Routes, Route} from 'react-router-dom';

import TopNavi from './components/TopNavi';
import UseReducerExam from './components/UseReducerExam';
import UseContextExam from './components/UseContextExam';

function App(){
  return(<>
    <TopNavi></TopNavi>
    <Routes>
      <Route path='/' element={<UseReducerExam />}></Route>
      <Route path='/use-reducer' element={<UseReducerExam />}></Route>
      <Route path='/use-context' element={<UseContextExam />}></Route>
    </Routes>
  </>)
}

export default App;