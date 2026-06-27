import { useMemo, useState } from 'react';

const seedPlayers = [
  { id: 1, nickname: 'Nova', country: 'KR', score: 12840, matches: 42, streak: 9 },
  { id: 2, nickname: 'Pixel', country: 'US', score: 11920, matches: 39, streak: 7 },
  { id: 3, nickname: 'Comet', country: 'JP', score: 11450, matches: 37, streak: 6 },
  { id: 4, nickname: 'Blitz', country: 'DE', score: 10860, matches: 34, streak: 5 },
  { id: 5, nickname: 'Luna', country: 'FR', score: 9950, matches: 30, streak: 4 },
];

const countryOptions = ['KR', 'US', 'JP', 'DE', 'FR', 'BR'];

function PlayerEditor({ onCreate }) {
  const [player, setPlayer] = useState({ nickname: '', country: 'KR', score: '', matches: '', streak: '' });

  const updateField = (event) => {
    const { name, value } = event.target;
    setPlayer((currentPlayer) => ({ ...currentPlayer, [name]: value }));
  };

  const submitPlayer = (event) => {
    event.preventDefault();

    if (!player.nickname.trim() || !player.score || !player.matches || !player.streak) {
      return;
    }

    onCreate({
      nickname: player.nickname.trim(),
      country: player.country,
      score: Number(player.score),
      matches: Number(player.matches),
      streak: Number(player.streak),
    });
    setPlayer({ nickname: '', country: 'KR', score: '', matches: '', streak: '' });
  };

  return (
    <form className="player-editor" onSubmit={submitPlayer}>
      <label>
        닉네임
        <input name="nickname" value={player.nickname} onChange={updateField} placeholder="Player name" />
      </label>
      <label>
        국가
        <select name="country" value={player.country} onChange={updateField}>
          {countryOptions.map((country) => (
            <option key={country} value={country}>{country}</option>
          ))}
        </select>
      </label>
      <label>
        점수
        <input name="score" type="number" min="0" value={player.score} onChange={updateField} />
      </label>
      <label>
        경기 수
        <input name="matches" type="number" min="0" value={player.matches} onChange={updateField} />
      </label>
      <label>
        연승
        <input name="streak" type="number" min="0" value={player.streak} onChange={updateField} />
      </label>
      <button type="submit">선수 추가</button>
    </form>
  );
}

function Podium({ leaders }) {
  return (
    <section className="podium" aria-label="상위 3명">
      {leaders.map((leader, index) => (
        <article key={leader.id} className={`podium-card rank-${index + 1}`}>
          <span className="medal">{index + 1}</span>
          <strong>{leader.nickname}</strong>
          <small>{leader.country} · {leader.score.toLocaleString()} pts</small>
        </article>
      ))}
    </section>
  );
}

function RankingTable({ players }) {
  return (
    <section className="ranking-panel">
      <div className="panel-title">
        <p>Leaderboard</p>
        <h2>전체 순위</h2>
      </div>
      <div className="table-scroller">
        <table>
          <thead>
            <tr>
              <th>Rank</th>
              <th>Player</th>
              <th>Country</th>
              <th>Score</th>
              <th>Matches</th>
              <th>Streak</th>
            </tr>
          </thead>
          <tbody>
            {players.map((player, index) => (
              <tr key={player.id}>
                <td><span className="rank-pill">#{index + 1}</span></td>
                <td>{player.nickname}</td>
                <td>{player.country}</td>
                <td>{player.score.toLocaleString()}</td>
                <td>{player.matches}</td>
                <td>{player.streak}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function App() {
  const [players, setPlayers] = useState(seedPlayers);

  const rankedPlayers = useMemo(() => {
    return [...players].sort((a, b) => {
      if (b.score !== a.score) {
        return b.score - a.score;
      }
      return b.streak - a.streak;
    });
  }, [players]);

  const topPlayer = rankedPlayers[0];
  const averageScore = Math.round(players.reduce((total, player) => total + player.score, 0) / players.length);

  const createPlayer = (newPlayer) => {
    setPlayers((currentPlayers) => [
      ...currentPlayers,
      { ...newPlayer, id: crypto.randomUUID() },
    ]);
  };

  return (
    <main className="page-shell">
      <section className="hero">
        <div>
          <p className="eyebrow">Season 2026</p>
          <h1>글로벌 게임 리더보드</h1>
          <p className="hero-description">
            플레이어 점수와 연승 기록을 기준으로 순위를 자동 계산하고, 새로운 선수를 바로 등록할 수 있습니다.
          </p>
        </div>
        <aside className="champion-card">
          <span>현재 챔피언</span>
          <strong>{topPlayer.nickname}</strong>
          <small>{topPlayer.score.toLocaleString()} pts · {topPlayer.streak}연승</small>
        </aside>
      </section>

      <section className="summary-grid" aria-label="시즌 요약">
        <article>
          <span>Players</span>
          <strong>{players.length}</strong>
        </article>
        <article>
          <span>Average score</span>
          <strong>{averageScore.toLocaleString()}</strong>
        </article>
        <article>
          <span>Top streak</span>
          <strong>{Math.max(...players.map((player) => player.streak))}</strong>
        </article>
      </section>

      <Podium leaders={rankedPlayers.slice(0, 3)} />

      <section className="editor-panel">
        <div className="panel-title">
          <p>Register</p>
          <h2>새 선수 등록</h2>
        </div>
        <PlayerEditor onCreate={createPlayer} />
      </section>

      <RankingTable players={rankedPlayers} />
    </main>
  );
}

export default App;
