import { useState } from 'react';
import useStudentStore from './useStudentStore';
import StudentUnit from './StudentUnit';


function AttendanceApp() {
  const [name, setName] = useState('')
  const {students, count, addStudent} = useStudentStore();
  return(<>
    <h2>출결 관리APP</h2>
    <p>총학생 수: {count}</p>
    <input 
    type="text"
    placeholder='이름을 입력하세요'
    value={name}
    onChange={(e) => setName(e.target.value)}
    />
    <button onClick={() => {
      if (name.trim()) {
        addStudent(name);
        setName('');
      }
    }}>추가</button>
    <ol>
      {students.map((student) => (
        <StudentUnit key={student.id} {...student} />
      ))}
    </ol>
  </>);
}

export default AttendanceApp;