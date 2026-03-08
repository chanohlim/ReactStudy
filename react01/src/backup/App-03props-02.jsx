function MyComponent({p1, p2, p3, p4}) {
  return (<>
    <h2>props 객체 사용</h2>
    <p>
      {p1}, {p2}, {p3}, {p4}
    </p>
  </>)
}

function App(){
  return(<>
    <MyComponent p1={'HTML'} p2={'CSS3'} p3={'JavaScript'} p4={'jQuery'} />
  </>)
}

export default App