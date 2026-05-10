import {Routes, Route} from "react-router-dom";

import Home from './components/Home';
import TopNavi from './components/TopNavi';
import NotFound from './components/NotFound';

function App() {
  return(<>
    <TopNavi></TopNavi>
    <Routes>
      <Route path='/' element={<Home />}></Route>
      <Route path='*' element={<NotFound />} />
    </Routes>
  </>)
}

export default App;