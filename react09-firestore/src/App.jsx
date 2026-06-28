import {Routes, Route} from 'react-router-dom';

import TopNavi from './components/TopNavi';
import FireConnect from './firestores/FireConnect';
// import FireCreate from './firestores/FireCreate';
// import FireRead from './firestores/FireRead';
// import FireUpdate from './firestores/FireUpdate';


function App(){
  return(<>
    <TopNavi></TopNavi>
    <Routes>
      <Route path='/' element={<FireConnect />} />
      <Route path='/connect' element={<FireConnect />} />
      {/* <Route path='/create' element={<FireCreate />} /> */}
      {/* <Route path='/read' element={<FireRead />} /> */}
      {/* <Route path='/update'> */}
        {/* <Route path=':userid' element={<FireUpdate></FireUpdate>}></Route> */}
      {/* </Route> */}
    </Routes>
  </>)
}

export default App;