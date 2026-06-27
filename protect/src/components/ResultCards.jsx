import { useSelector } from 'react-redux';
import { formatMinutes } from '../utils/timeAnalysis';

const riskClass = {
  안전: 'safe',
  주의: 'watch',
  위험: 'danger',
  심각: 'critical',
};

function ResultCards() {
  const { result } = useSelector((state) => state.workDefense);

  return (
    <section className="panel" aria-labelledby="result-title">
      <div className="section-heading">
        <p className="eyebrow">Step 2</p>
        <h2 id="result-title">분석 결과</h2>
      </div>

      <div className="result-grid">
        <article className="metric-card">
          <span>퇴근까지 남은 시간</span>
          <strong>{formatMinutes(result.remainingMinutes)}</strong>
        </article>
        <article className="metric-card">
          <span>예상 소요 시간</span>
          <strong>{formatMinutes(result.estimatedMinutes)}</strong>
        </article>
        <article className="metric-card">
          <span>근무시간 내 완료</span>
          <strong>{result.canFinishInWorkHours ? '가능' : '어려움'}</strong>
        </article>
        <article className="metric-card">
          <span>초과 예상 시간</span>
          <strong>{formatMinutes(result.overtimeMinutes)}</strong>
        </article>
      </div>

      <div className={`risk-banner ${riskClass[result.riskLevel]}`}>
        <span>야근 위험도</span>
        <strong>{result.riskLevel}</strong>
        <p>{result.summary}</p>
      </div>

      <p className="last-minute">
        {result.isLastMinuteRequest ? '⏰ 퇴근 직전 요청으로 보입니다. 방어 멘트를 장착하세요.' : '🛡️ 아직 협의할 시간이 있습니다. 차분하게 우선순위를 확인하세요.'}
      </p>
    </section>
  );
}

export default ResultCards;
