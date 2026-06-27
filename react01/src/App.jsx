import { useMemo, useState } from 'react';

const initialPlayers = [
  { id: 1, name: '김민준', team: '프론트엔드', score: 9840, wins: 31 },
  { id: 2, name: '이서연', team: '백엔드', score: 9320, wins: 28 },
  { id: 3, name: '박지훈', team: '디자인', score: 8870, wins: 24 },
  { id: 4, name: '최하린', team: '기획', score: 8510, wins: 22 },
  { id: 5, name: '정도윤', team: '프론트엔드', score: 8120, wins: 19 },
  { id: 6, name: '한유진', team: '백엔드', score: 7760, wins: 18 },
];

function PlayerForm({ onAddPlayer }) {
  const [form, setForm] = useState({ name: '', team: '프론트엔드', score: '', wins: '' });

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((prevForm) => ({ ...prevForm, [name]: value }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();

    if (!form.name.trim() || !form.score || !form.wins) {
      return;
    }

    onAddPlayer({
      name: form.name.trim(),
      team: form.team,
      score: Number(form.score),
      wins: Number(form.wins),
    });
    setForm({ name: '', team: '프론트엔드', score: '', wins: '' });
  };

  return (
    <form className="player-form" onSubmit={handleSubmit}>
      <label>
        참가자
        <input
          name="name"
          type="text"
          value={form.name}
          onChange={handleChange}
          placeholder="이름 입력"
        />
      </label>
      <label>
        팀
        <select name="team" value={form.team} onChange={handleChange}>
          <option value="프론트엔드">프론트엔드</option>
          <option value="백엔드">백엔드</option>
          <option value="디자인">디자인</option>
          <option value="기획">기획</option>
        </select>
      </label>
      <label>
        점수
        <input
          name="score"
          type="number"
          min="0"
          value={form.score}
          onChange={handleChange}
          placeholder="0"
        />
      </label>
      <label>
        승수
        <input
          name="wins"
          type="number"
          min="0"
          value={form.wins}
          onChange={handleChange}
          placeholder="0"
        />
      </label>
      <button type="submit">등록하기</button>
    </form>
  );
}

function Leaderboard({ players }) {
  return (
    <section className="leaderboard-card" aria-labelledby="leaderboard-title">
      <div className="section-heading">
        <p>Live ranking</p>
        <h2 id="leaderboard-title">실시간 리더보드</h2>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>순위</th>
              <th>참가자</th>
              <th>팀</th>
              <th>점수</th>
              <th>승수</th>
            </tr>
          </thead>
          <tbody>
            {players.map((player, index) => (
              <tr key={player.id} className={index < 3 ? 'podium-row' : ''}>
                <td>
                  <span className="rank-badge">#{index + 1}</span>
                </td>
                <td>{player.name}</td>
                <td>{player.team}</td>
                <td>{player.score.toLocaleString()}</td>
                <td>{player.wins}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function App() {
  const [players, setPlayers] = useState(initialPlayers);

  const rankedPlayers = useMemo(() => {
    return [...players].sort((first, second) => {
      if (second.score !== first.score) {
        return second.score - first.score;
      }
      return second.wins - first.wins;
    });
  }, [players]);

  const topPlayer = rankedPlayers[0];
  const totalScore = players.reduce((sum, player) => sum + player.score, 0);

  const addPlayer = (newPlayer) => {
    setPlayers((prevPlayers) => [
      ...prevPlayers,
      { ...newPlayer, id: Date.now() },
    ]);
  };

  return (
    <main className="app-shell">
      <section className="hero-card">
        <div>
          <p className="eyebrow">React Leaderboard</p>
          <h1>팀 챌린지 리더보드</h1>
          <p className="hero-copy">
            점수와 승수를 기준으로 참가자 순위를 자동 정렬하는 리액트 리더보드 웹 서비스입니다.
          </p>
        </div>
        <div className="winner-card">
          <span>현재 1위</span>
          <strong>{topPlayer.name}</strong>
          <small>{topPlayer.score.toLocaleString()}점 · {topPlayer.wins}승</small>
        </div>
      </section>

      <section className="stats-grid" aria-label="리더보드 요약">
        <article>
          <span>참가자</span>
          <strong>{players.length}명</strong>
        </article>
        <article>
          <span>총점</span>
          <strong>{totalScore.toLocaleString()}</strong>
        </article>
        <article>
          <span>최고 점수</span>
          <strong>{topPlayer.score.toLocaleString()}</strong>
        </article>
      </section>

      <section className="form-card" aria-labelledby="form-title">
        <div className="section-heading">
          <p>New challenger</p>
          <h2 id="form-title">참가자 추가</h2>
        </div>
        <PlayerForm onAddPlayer={addPlayer} />
      </section>

      <Leaderboard players={rankedPlayers} />
    </main>
  );
}

export default App;
