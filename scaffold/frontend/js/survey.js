const SURVEY_QUESTIONS = [
  {
    text: '새로운 사람을 만나는 날, 거울 앞의 나는?',
    opts: [
      { key: 'A', text: '깔끔하고 단정하게! 지적이면서 세련된 인상 주고 싶어 ✨', sc: ['소피스티케이티드', '모던/미니멀', '매니시'] },
      { key: 'B', text: '부드럽고 편안하게! 금방 친해지고 싶은 사람처럼 보이고 싶어 ✌️', sc: ['캐주얼', '로맨틱', '페미닌'] }
    ]
  },
  {
    text: '온라인 쇼핑 중 더 눈길이 가는 옷은?',
    opts: [
      { key: 'A', text: '오래 입을 수 있는 기본템, 군더더기 없는 실루엣, 담백한 색감', sc: ['모던/미니멀', '캐주얼', '소피스티케이티드'] },
      { key: 'B', text: '한눈에 포인트가 보이는 아이템, 독특한 디테일, 눈에 띄는 분위기', sc: ['스트리트', '힙스터/펑크', '레트로/빈티지'] }
    ]
  },
  {
    text: '배가 살짝 부른 상태! 지금 내 옷의 핏은?',
    opts: [
      { key: 'A', text: '핏이 무너지면 안 되지! 꼼꼼히 읽고 딱 맞는 정사이즈로 📏', sc: [] },
      { key: 'B', text: '작은 것보단 큰 게 낫지! 한 사이즈 크게 넉넉하게 입는다 👕', sc: [] }
    ]
  },
  {
    text: '가장 기분 좋은 주말 외출은?',
    opts: [
      { key: 'A', text: '예쁜 카페에서 커피, 핫플에서 예쁜 사진 남기는 코스 📸', sc: ['페미닌', '로맨틱', '레트로/빈티지'] },
      { key: 'B', text: '산책, 피크닉, 여기저기 뽈뽈거리며 돌아다니는 활동적인 코스', sc: ['스포티', '스트리트', '캐주얼'] }
    ]
  },
  {
    text: '오랜만의 문화생활! 더 끌리는 영화 포스터는?',
    opts: [
      { key: 'A', text: '차갑고 도시적인 장면, 절제된 톤, 시크한 주인공 🌃', sc: ['매니시', '모던/미니멀', '스트리트'] },
      { key: 'B', text: '빈티지한 햇살, 감성적인 장면, 몽글몽글한 로맨스 무드 ❤️', sc: ['로맨틱', '레트로/빈티지', '페미닌'] }
    ]
  },
  {
    text: '옷에서 좋아하는 포인트는?',
    opts: [
      { key: 'A', text: '로고나 패턴 없이 심플하고 색감이 깔끔한 기본템 🤍', sc: ['소피스티케이티드', '매니시', '모던/미니멀'] },
      { key: 'B', text: '흔하지 않은 디자인, 톡톡 튀는 컬러, 유니크한 포인트템 💖', sc: ['힙스터/펑크', '스트리트', '스포티'] }
    ]
  },
  {
    text: '더 편하게 느끼는 코디 방식은?',
    opts: [
      { key: 'A', text: '힘 빼고 자연스럽지만, 보기엔 센스 있는 꾸안꾸 스타일', sc: ['캐주얼', '스포티', '힙스터/펑크'] },
      { key: 'B', text: '무드가 분명하고, 분위기 자체가 예쁘게 완성되는 스타일', sc: ['페미닌', '로맨틱', '소피스티케이티드'] }
    ]
  },
  {
    text: '남들이 내 옷을 보고 해줬으면 하는 말은?',
    opts: [
      { key: 'A', text: '"와, 되게 멋있다. 자기 스타일 확실하다."', sc: ['매니시', '힙스터/펑크', '스트리트'] },
      { key: 'B', text: '"와, 분위기 있다. 되게 센스 있고 예쁘다."', sc: ['모던/미니멀', '레트로/빈티지', '스포티'] }
    ]
  },
  {
    text: '오늘 중요한 약속! 옷 고를 때 가장 먼저 드는 생각은?',
    opts: [
      { key: 'A', text: '어디서든 자연스럽게 어울리는 단정하고 무난한 스타일로', sc: ['소피스티케이티드', '모던/미니멀'] },
      { key: 'B', text: '사람들 만나는 자리니까 예쁘고 호감 가게 입고 싶어!', sc: ['페미닌', '로맨틱'] },
      { key: 'C', text: '격식 있는 자리니까 신경 써서 갖춰 입어야 해!', sc: ['소피스티케이티드', '매니시'] },
      { key: 'D', text: '오래 돌아다닐 거니까 편하고 활동성 있게 입자!', sc: ['스포티', '캐주얼'] }
    ]
  }
];

let surveyState = requireState(['gender', 'personalColor'], './index.html');

function renderSurvey() {
  if (!surveyState) return;

  const question = SURVEY_QUESTIONS[surveyState.currentQ];
  const saved = surveyState.surveyAnswers[surveyState.currentQ];
  const pct = Math.round(((surveyState.currentQ + 1) / SURVEY_QUESTIONS.length) * 100);

  qs('#q-prog-txt').textContent = `Q${surveyState.currentQ + 1} / ${SURVEY_QUESTIONS.length}`;
  qs('#q-prog-pct').textContent = `${pct}%`;
  qs('#pbar').style.width = `${pct}%`;
  qs('#q-num').textContent = `Q${surveyState.currentQ + 1}`;
  qs('#q-text').textContent = question.text;
  qs('#survey-next').textContent = surveyState.currentQ === SURVEY_QUESTIONS.length - 1 ? '결과 보기 🎉' : '다음 →';

  qs('#q-options').innerHTML = question.opts.map((option) => {
    const selected = saved === option.key;
    return `
      <button class="option-btn ${selected ? 'is-selected' : ''}" data-answer="${option.key}">
        <span class="option-key">${option.key}</span>
        <span style="flex:1;">${option.text}</span>
        ${selected ? '<span class="option-check">✔ 선택</span>' : ''}
      </button>
    `;
  }).join('');

  qsa('[data-answer]').forEach((button) => {
    button.addEventListener('click', () => selectAnswer(button.dataset.answer));
  });
}

function selectAnswer(answerKey) {
  surveyState.surveyAnswers[surveyState.currentQ] = answerKey;
  surveyState = patchAppState({ surveyAnswers: surveyState.surveyAnswers });
  renderSurvey();
}

function goPrev() {
  if (surveyState.currentQ === 0) {
    navigateTo('./index.html');
    return;
  }

  surveyState = patchAppState({ currentQ: surveyState.currentQ - 1 });
  renderSurvey();
}

function calcResult() {
  const scores = {};
  Object.keys(PERSONAS).forEach((key) => {
    scores[key] = 0;
  });

  SURVEY_QUESTIONS.forEach((question, index) => {
    const answer = surveyState.surveyAnswers[index];
    if (!answer) return;
    const selected = question.opts.find((opt) => opt.key === answer);
    (selected?.sc || []).forEach((name) => {
      scores[name] += 1;
    });
  });

  return getResultByScores(scores);
}

async function goNext() {
  if (!surveyState.surveyAnswers[surveyState.currentQ]) {
    alert('선택해주세요!');
    return;
  }

  if (surveyState.currentQ < SURVEY_QUESTIONS.length - 1) {
    surveyState = patchAppState({ currentQ: surveyState.currentQ + 1 });
    renderSurvey();
    return;
  }

  const result = calcResult();
  patchAppState({ result, currentQ: surveyState.currentQ });
  navigateTo('./result.html');
}

document.addEventListener('DOMContentLoaded', () => {
  if (!surveyState) return;
  renderSurvey();

  qs('#prev-btn').addEventListener('click', goPrev);
  qs('#survey-next').addEventListener('click', goNext);
});