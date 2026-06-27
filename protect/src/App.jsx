import './App.css';
import HistoryList from './components/HistoryList';
import ReplySuggestions from './components/ReplySuggestions';
import ResultCards from './components/ResultCards';
import TaskForm from './components/TaskForm';

function App() {
  return (
    <main className="app-shell">
      <section className="hero">
        <div>
          <p className="eyebrow">Work Defense Timer</p>
          <h1>퇴근 방어 타이머</h1>
          <p>퇴근 직전 업무 요청, 진짜 오늘 해야 할 일인지 계산해드립니다.</p>
        </div>
        <div className="hero-badge">칼퇴 확률 계산 중…</div>
      </section>

      <div className="content-grid">
        <TaskForm />
        <div className="stack">
          <ResultCards />
          <ReplySuggestions />
        </div>
      </div>

      <HistoryList />
    </main>
  );
}

export default App;
