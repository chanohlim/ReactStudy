<Routes>
  <Route path='경로A' element={<컴포넌트1 />} />
  <Route path='경로B'>
    <Route index element={<컴포넌트2 />} />
    <Route path='경로C' element={<컴포넌트3 />} />
  </Route>

</Routes>