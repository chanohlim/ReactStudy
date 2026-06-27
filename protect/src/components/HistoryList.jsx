import { useDispatch, useSelector } from 'react-redux';
import { deleteAnalysis } from '../features/workDefenseSlice';
import { formatMinutes } from '../utils/timeAnalysis';

function HistoryList() {
  const dispatch = useDispatch();
  const history = useSelector((state) => state.workDefense.history);

  return (
    <section className="panel history-panel" aria-labelledby="history-title">
      <div className="section-heading">
        <p className="eyebrow">Archive</p>
        <h2 id="history-title">이전 분석 기록</h2>
      </div>

      {history.length === 0 ? (
        <p className="empty-history">아직 저장된 기록이 없습니다. 오늘의 평화를 지키는 첫 분석을 저장해보세요.</p>
      ) : (
        <ul className="history-list">
          {history.map((item) => (
            <li key={item.id}>
              <div>
                <strong>{item.form.title || '제목 없는 업무'}</strong>
                <p>{item.result.riskLevel} · 초과 {formatMinutes(item.result.overtimeMinutes)} · {new Date(item.createdAt).toLocaleString('ko-KR')}</p>
              </div>
              <button type="button" className="ghost small" onClick={() => dispatch(deleteAnalysis(item.id))}>삭제</button>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

export default HistoryList;
