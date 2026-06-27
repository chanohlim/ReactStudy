import { useMemo, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  addDistraction,
  clearDistractions,
  removeDistraction,
  selectDistractionStats,
  selectRankedEntries,
} from './features/distractions/distractionsSlice';

const distractionTypes = [
  '유튜브 쇼츠',
  'SNS 탐험',
  '메신저 수다',
  '커피 산책',
  '간식 원정대',
  '창밖 멍때리기',
  '회의 중 딴생각',
];

function formatTime(minutes) {
  const hours = Math.floor(minutes / 60);
  const restMinutes = minutes % 60;

  if (hours === 0) {
    return `${restMinutes}분`;
  }

  return `${hours}시간 ${restMinutes}분`;
}

function DistractionForm() {
  const dispatch = useDispatch();
  const [form, setForm] = useState({ name: '', type: distractionTypes[0], minutes: '' });
  const isDisabled = !form.name.trim() || !form.minutes || Number(form.minutes) <= 0;

  const updateForm = (event) => {
    const { name, value } = event.target;
    setForm((currentForm) => ({ ...currentForm, [name]: value }));
  };

  const submitForm = (event) => {
    event.preventDefault();

    if (isDisabled) {
      return;
    }

    dispatch(addDistraction({
      name: form.name.trim(),
      type: form.type,
      minutes: Number(form.minutes),
    }));
    setForm({ name: '', type: distractionTypes[0], minutes: '' });
  };

  return (
    <form className="distraction-form" onSubmit={submitForm}>
      <label>
        이름
        <input
          name="name"
          type="text"
          value={form.name}
          onChange={updateForm}
          placeholder="예: 홍길동"
        />
      </label>
      <label>
        딴 짓 종류
        <select name="type" value={form.type} onChange={updateForm}>
          {distractionTypes.map((type) => (
            <option key={type} value={type}>{type}</option>
          ))}
        </select>
      </label>
      <label>
        시간(분)
        <input
          name="minutes"
          type="number"
          min="1"
          value={form.minutes}
          onChange={updateForm}
          placeholder="예: 45"
        />
      </label>
      <button type="submit" disabled={isDisabled}>리더보드 등록</button>
    </form>
  );
}

function StatCard({ label, value, helper }) {
  return (
    <article className="stat-card">
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{helper}</small>
    </article>
  );
}

function TopThree({ entries }) {
  return (
    <section className="podium" aria-label="딴 짓 상위 3명">
      {entries.slice(0, 3).map((entry, index) => (
        <article key={entry.id} className={`podium-card rank-${index + 1}`}>
          <span className="rank-number">#{index + 1}</span>
          <strong>{entry.name}</strong>
          <p>{entry.type}</p>
          <small>{formatTime(entry.minutes)}</small>
        </article>
      ))}
    </section>
  );
}

function LeaderboardTable({ entries }) {
  const dispatch = useDispatch();

  if (entries.length === 0) {
    return (
      <section className="empty-panel">
        <h2>아직 등록된 딴 짓이 없습니다</h2>
        <p>첫 번째 딴 짓 기록을 등록하면 리더보드가 바로 생성됩니다.</p>
      </section>
    );
  }

  return (
    <section className="table-panel">
      <div className="section-title">
        <p>Ranking</p>
        <h2>딴 짓 리더보드</h2>
      </div>
      <div className="table-scroll">
        <table>
          <thead>
            <tr>
              <th>순위</th>
              <th>이름</th>
              <th>딴 짓 종류</th>
              <th>시간</th>
              <th>등록 시각</th>
              <th>관리</th>
            </tr>
          </thead>
          <tbody>
            {entries.map((entry, index) => (
              <tr key={entry.id}>
                <td><span className="rank-pill">#{index + 1}</span></td>
                <td>{entry.name}</td>
                <td>{entry.type}</td>
                <td>{formatTime(entry.minutes)}</td>
                <td>{new Date(entry.createdAt).toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })}</td>
                <td>
                  <button className="delete-button" onClick={() => dispatch(removeDistraction(entry.id))}>
                    삭제
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function App() {
  const dispatch = useDispatch();
  const rankedEntries = useSelector(selectRankedEntries);
  const stats = useSelector(selectDistractionStats);
  const mostPopularType = useMemo(() => {
    const typeCounts = rankedEntries.reduce((counts, entry) => {
      counts[entry.type] = (counts[entry.type] || 0) + 1;
      return counts;
    }, {});

    return Object.entries(typeCounts).sort((a, b) => b[1] - a[1])[0]?.[0] || '집계 중';
  }, [rankedEntries]);

  return (
    <main className="app-shell">
      <section className="hero-card">
        <div>
          <p className="eyebrow">팀장님 한숨 예약 서비스</p>
          <h1>딴 짓 리더보드</h1>
          <p className="hero-copy">
            이름, 딴 짓 종류, 시간을 입력하면 누가 가장 열심히 딴 짓을 했는지 즉시 순위로 보여줍니다.
            React와 Redux Toolkit으로 상태를 관리합니다.
          </p>
        </div>
        <aside className="leader-card">
          <span>현재 딴짓왕</span>
          <strong>{stats.topEntry?.name || '대기 중'}</strong>
          <small>{stats.topEntry ? `${stats.topEntry.type} · ${formatTime(stats.topEntry.minutes)}` : '기록을 등록해 주세요'}</small>
        </aside>
      </section>

      <section className="stats-grid" aria-label="딴 짓 요약">
        <StatCard label="총 딴 짓 시간" value={formatTime(stats.totalMinutes)} helper="누적 시간" />
        <StatCard label="평균 딴 짓" value={formatTime(stats.averageMinutes)} helper={`${stats.entryCount}건 기준`} />
        <StatCard label="인기 딴 짓" value={mostPopularType} helper="가장 자주 등록됨" />
      </section>

      <section className="form-panel">
        <div className="section-title">
          <p>Register</p>
          <h2>딴 짓 기록 추가</h2>
        </div>
        <DistractionForm />
      </section>

      <TopThree entries={rankedEntries} />

      <div className="toolbar">
        <p>점수가 아니라 시간으로 승부합니다. 오래 딴 짓할수록 위로 올라갑니다.</p>
        <button type="button" onClick={() => dispatch(clearDistractions())}>전체 초기화</button>
      </div>

      <LeaderboardTable entries={rankedEntries} />
    </main>
  );
}

export default App;
