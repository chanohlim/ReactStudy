const TIME_PATTERN = /^([01]\d|2[0-3]):([0-5]\d)$/;

export const DEFAULT_RESULT = {
  remainingMinutes: 0,
  estimatedMinutes: 0,
  canFinishInWorkHours: false,
  overtimeMinutes: 0,
  riskLevel: '주의',
  isLastMinuteRequest: false,
  messages: ['업무 정보를 입력한 뒤 분석하기를 눌러 퇴근 방어 전략을 확인해보세요.'],
  summary: '아직 분석 전입니다.',
  error: '',
};

export function timeToMinutes(timeText) {
  if (typeof timeText !== 'string' || !TIME_PATTERN.test(timeText)) {
    return null;
  }

  const [hours, minutes] = timeText.split(':').map(Number);
  return hours * 60 + minutes;
}

export function formatMinutes(totalMinutes) {
  const safeMinutes = Math.max(0, Number.isFinite(totalMinutes) ? totalMinutes : 0);
  const hours = Math.floor(safeMinutes / 60);
  const minutes = safeMinutes % 60;

  if (hours === 0) return `${minutes}분`;
  if (minutes === 0) return `${hours}시간`;
  return `${hours}시간 ${minutes}분`;
}

function getRiskLevel({ overtimeMinutes, urgency, requiredToday, isLastMinuteRequest }) {
  if (overtimeMinutes >= 120 || (requiredToday && urgency === '높음' && overtimeMinutes > 0)) {
    return '심각';
  }

  if (overtimeMinutes > 0 || (urgency === '높음' && isLastMinuteRequest)) {
    return '위험';
  }

  if (isLastMinuteRequest || urgency === '보통') {
    return '주의';
  }

  return '안전';
}

function buildMessages({ form, remainingMinutes, overtimeMinutes, canFinishInWorkHours, riskLevel }) {
  const messages = [];
  const taskName = form.title?.trim() || '요청 주신 업무';

  if (!canFinishInWorkHours) {
    messages.push(`현재 퇴근까지 남은 시간이 부족하여 “${taskName}”은 오늘 착수만 가능하고, 완료는 내일 오전 중으로 예상됩니다.`);
    messages.push('예상 소요 시간이 정규 근무시간을 초과하므로 일정 조정 또는 업무 범위 조정이 필요해 보입니다.');
  } else {
    messages.push(`퇴근 전 남은 시간 안에 “${taskName}” 처리가 가능해 보입니다. 우선 필요한 범위부터 확인해 바로 진행하겠습니다.`);
  }

  if (form.requiredToday) {
    messages.push('오늘 반드시 완료해야 하는 핵심 범위와 내일 처리 가능한 항목을 구분해주시면 우선순위에 맞춰 진행하겠습니다.');
  } else {
    messages.push('오늘 중 긴급 완료가 필수인 항목이 아니라면, 품질을 위해 내일 업무 시간에 이어서 처리하겠습니다.');
  }

  if (riskLevel === '심각') {
    messages.push(`초과 예상 시간이 ${formatMinutes(overtimeMinutes)}라서, 담당 범위 조정이나 마감 시간 재협의가 필요합니다.`);
  } else if (remainingMinutes <= 30) {
    messages.push('퇴근 직전 요청이라 현재 가능한 범위와 내일 이어서 처리할 범위를 먼저 정리해 공유드리겠습니다.');
  }

  return messages;
}

export function analyzeWorkDefense(form) {
  const requestMinutes = timeToMinutes(form.requestTime);
  const finishMinutes = timeToMinutes(form.finishTime);
  const estimatedMinutes = Number.parseInt(form.estimatedMinutes, 10);

  if (requestMinutes === null || finishMinutes === null) {
    return { ...DEFAULT_RESULT, error: '업무 요청 시각과 정규 퇴근 시각을 HH:MM 형식으로 입력해주세요.' };
  }

  if (!Number.isFinite(estimatedMinutes) || estimatedMinutes <= 0) {
    return { ...DEFAULT_RESULT, error: '예상 소요 시간은 1분 이상으로 입력해주세요.' };
  }

  const remainingMinutes = Math.max(0, finishMinutes - requestMinutes);
  const overtimeMinutes = Math.max(0, estimatedMinutes - remainingMinutes);
  const canFinishInWorkHours = overtimeMinutes === 0;
  const isLastMinuteRequest = remainingMinutes <= 30;
  const riskLevel = getRiskLevel({
    overtimeMinutes,
    urgency: form.urgency,
    requiredToday: form.requiredToday,
    isLastMinuteRequest,
  });

  return {
    remainingMinutes,
    estimatedMinutes,
    canFinishInWorkHours,
    overtimeMinutes,
    riskLevel,
    isLastMinuteRequest,
    messages: buildMessages({ form, remainingMinutes, overtimeMinutes, canFinishInWorkHours, riskLevel }),
    summary: canFinishInWorkHours
      ? '정규 근무시간 안에 방어 성공 가능성이 높습니다.'
      : `정규 근무시간을 ${formatMinutes(overtimeMinutes)} 초과할 수 있습니다.`,
    error: '',
  };
}
