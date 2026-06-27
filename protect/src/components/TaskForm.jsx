import { useDispatch, useSelector } from 'react-redux';
import { analyzeTask, resetForm, saveAnalysis, updateField } from '../features/workDefenseSlice';

function TaskForm() {
  const dispatch = useDispatch();
  const { form, result } = useSelector((state) => state.workDefense);

  const handleChange = (event) => {
    const { name, value, type, checked } = event.target;
    dispatch(updateField({ field: name, value: type === 'checkbox' ? checked : value }));
  };

  return (
    <section className="panel form-panel" aria-labelledby="form-title">
      <div className="section-heading">
        <p className="eyebrow">Step 1</p>
        <h2 id="form-title">업무 요청 입력</h2>
      </div>

      <div className="form-grid">
        <label>
          업무 제목
          <input name="title" value={form.title} onChange={handleChange} placeholder="예: 월간 보고서 긴급 수정" />
        </label>
        <label>
          긴급도
          <select name="urgency" value={form.urgency} onChange={handleChange}>
            <option>낮음</option>
            <option>보통</option>
            <option>높음</option>
          </select>
        </label>
        <label className="wide">
          업무 설명
          <textarea name="description" value={form.description} onChange={handleChange} placeholder="요청받은 내용과 완료 기준을 간단히 적어주세요." rows="4" />
        </label>
        <label>
          업무 요청 시각
          <input type="time" name="requestTime" value={form.requestTime} onChange={handleChange} />
        </label>
        <label>
          정규 퇴근 시각
          <input type="time" name="finishTime" value={form.finishTime} onChange={handleChange} />
        </label>
        <label>
          예상 소요 시간(분)
          <input type="number" min="1" name="estimatedMinutes" value={form.estimatedMinutes} onChange={handleChange} />
        </label>
        <label className="check-card">
          <input type="checkbox" name="requiredToday" checked={form.requiredToday} onChange={handleChange} />
          오늘 반드시 필요한 업무입니다
        </label>
      </div>

      {result.error && <p className="error-message">{result.error}</p>}

      <div className="button-row">
        <button type="button" className="primary" onClick={() => dispatch(analyzeTask())}>분석하기</button>
        <button type="button" onClick={() => dispatch(saveAnalysis())}>기록 저장</button>
        <button type="button" className="ghost" onClick={() => dispatch(resetForm())}>초기화</button>
      </div>
    </section>
  );
}

export default TaskForm;
