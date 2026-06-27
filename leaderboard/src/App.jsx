import { useState } from 'react';
import { useDispatch, useSelector } from './lib/reactRedux.jsx';
import {
  addDistraction,
  addDistractionType,
  clearDistractions,
  removeDistraction,
  removePerson,
  selectDistractionStats,
  selectDistractionTypes,
  selectRankedPeople,
} from './features/distractions/distractionsSlice';

function formatTime(minutes) {
  const hours = Math.floor(minutes / 60);
  const restMinutes = minutes % 60;

  if (hours === 0) {
    return `${restMinutes}분`;
  }

  return `${hours}시간 ${restMinutes}분`;
}

function DistractionTypeManager() {
  const dispatch = useDispatch();
  const types = useSelector(selectDistractionTypes);
  const [newType, setNewType] = useState('');
  const normalizedNewType = newType.trim().toLocaleLowerCase('ko-KR');
  const isDuplicate = types.some((type) => type.trim().toLocaleLowerCase('ko-KR') === normalizedNewType);
  const isDisabled = !newType.trim() || isDuplicate;

  const submitType = (event) => {
    event.preventDefault();

    if (isDisabled) {
      return;
    }

    dispatch(addDistractionType(newType));
    setNewType('');
  };

  return (
    <form className="type-manager" onSubmit={submitType}>
      <label>
        새로운 딴 짓 등록
        <input
          value={newType}
          onChange={(event) => setNewType(event.target.value)}
          placeholder="예: 탕비실 회의"
        />
      </label>
      <button type="submit" disabled={isDisabled}>종류 추가</button>
      {isDuplicate && <p className="form-hint">이미 등록된 딴 짓입니다.</p>}
    </form>
  );
}

function DistractionForm() {
  const dispatch = useDispatch();
  const types = useSelector(selectDistractionTypes);
  const [form, setForm] = useState({ name: '', type: types[0] || '', customType: '', minutes: '' });
  const selectedType = form.type === 'custom' ? form.customType : form.type;
  const isDisabled = !form.name.trim() || !selectedType.trim() || !form.minutes || Number(form.minutes) <= 0;

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
      name: form.name,
      type: selectedType,
      minutes: Number(form.minutes),
    }));
    setForm({ name: '', type: types[0] || '', customType: '', minutes: '' });
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
          {types.map((type) => (
            <option key={type} value={type}>{type}</option>
          ))}
          <option value="custom">직접 입력</option>
        </select>
      </label>
      {form.type === 'custom' && (
        <label>
          직접 입력
          <input
            name="customType"
            type="text"
            value={form.customType}
            onChange={updateForm}
            placeholder="새 딴 짓 이름"
          />
        </label>
      )}
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

function TopThree({ people }) {
  return (
    <section className="podium" aria-label="딴 짓 상위 3명">
      {people.slice(0, 3).map((person, index) => (
        <article key={person.id} className={`podium-card rank-${index + 1}`}>
          <span className="rank-number">#{index + 1}</span>
          <strong>{person.name}</strong>
          <p>{person.topDistraction.type} · {formatTime(person.topDistraction.minutes)}</p>
          <small>총 {formatTime(person.totalMinutes)} · {person.distractions.length}종 딴 짓</small>
        </article>
      ))}
    </section>
  );
}

function DistractionChips({ person }) {
  const dispatch = useDispatch();

  return (
    <div className="chip-list" aria-label={`${person.name} 딴 짓 목록`}>
      {person.distractions.map((distraction) => (
        <span className="distraction-chip" key={distraction.id}>
          {distraction.type} {formatTime(distraction.minutes)}
          <button
            type="button"
            onClick={() => dispatch(removeDistraction({ personId: person.id, distractionId: distraction.id }))}
            aria-label={`${person.name}의 ${distraction.type} 삭제`}
          >
            ×
          </button>
        </span>
      ))}
    </div>
  );
}

function LeaderboardTable({ people }) {
  const dispatch = useDispatch();

  if (people.length === 0) {
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
              <th>딴 짓 내역</th>
              <th>총 시간</th>
              <th>관리</th>
            </tr>
          </thead>
          <tbody>
            {people.map((person, index) => (
              <tr key={person.id}>
                <td><span className="rank-pill">#{index + 1}</span></td>
                <td>{person.name}</td>
                <td><DistractionChips person={person} /></td>
                <td>{formatTime(person.totalMinutes)}</td>
                <td>
                  <button className="delete-button" onClick={() => dispatch(removePerson(person.id))}>
                    사람 삭제
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
  const rankedPeople = useSelector(selectRankedPeople);
  const stats = useSelector(selectDistractionStats);

  return (
    <main className="app-shell">
      <section className="hero-card">
        <div>
          <p className="eyebrow">팀장님 한숨 예약 서비스</p>
          <h1>딴 짓 리더보드</h1>
          <p className="hero-copy">
            같은 이름으로 기록하면 한 사람의 딴 짓 내역에 누적됩니다. 같은 딴 짓은 시간이 더해지고,
            처음 하는 딴 짓은 새 항목으로 추가됩니다.
          </p>
        </div>
        <aside className="leader-card">
          <span>현재 딴짓왕</span>
          <strong>{stats.topPerson?.name || '대기 중'}</strong>
          <small>{stats.topPerson ? `총 ${formatTime(stats.topPerson.totalMinutes)}` : '기록을 등록해 주세요'}</small>
        </aside>
      </section>

      <section className="stats-grid" aria-label="딴 짓 요약">
        <StatCard label="총 딴 짓 시간" value={formatTime(stats.totalMinutes)} helper="누적 시간" />
        <StatCard label="평균 딴 짓" value={formatTime(stats.averageMinutes)} helper={`${stats.personCount}명 기준`} />
        <StatCard label="인기 딴 짓" value={stats.topType} helper={`${stats.distractionCount}개 항목 집계`} />
      </section>

      <section className="form-panel">
        <div className="section-title">
          <p>Register</p>
          <h2>딴 짓 기록 추가</h2>
        </div>
        <DistractionForm />
        <DistractionTypeManager />
      </section>

      <TopThree people={rankedPeople} />

      <div className="toolbar">
        <p>동명이인은 같은 사람으로 합산됩니다. 이름을 정확히 입력하면 딴 짓 이력이 자동으로 정리됩니다.</p>
        <button type="button" onClick={() => dispatch(clearDistractions())}>전체 초기화</button>
      </div>

      <LeaderboardTable people={rankedPeople} />
    </main>
  );
}

export default App;
