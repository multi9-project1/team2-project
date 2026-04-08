(function (window) {
  const utils = window.MapsiUtils;
  const api = window.MapsiApi || {};

  const COLORS = [
    { key: '봄 라이트', dot: '#FFE8C4', bg: '#FFFDE7', desc: '밝고 연한 파스텔.' },
    { key: '봄 브라이트', dot: '#FFB347', bg: '#FFE0B2', desc: '선명하고 생기 있는.' },
    { key: '봄 웜', dot: '#FFCC88', bg: '#FFF3E0', desc: '따뜻한 복숭아 베이스.' },
    { key: '여름 라이트', dot: '#B8D8F8', bg: '#E3F2FD', desc: '연하고 차가운 파스텔.' },
    { key: '여름 뮤트', dot: '#8BAABF', bg: '#BBDEFB', desc: '차분하고 오묘한 회색빛.' },
    { key: '여름 쿨', dot: '#6699CC', bg: '#C5CAE9', desc: '밝고 선명한 쿨 계열.' },
    { key: '가을 뮤트', dot: '#C8A878', bg: '#FFE0B2', desc: '채도 낮은 카키와 올리브.' },
    { key: '가을 딥', dot: '#8B5E3C', bg: '#EFEBE9', desc: '깊고 진한 버건디와 브라운.' },
    { key: '가을 웜', dot: '#CC8844', bg: '#FFF3E0', desc: '클래식하고 따뜻한 어스톤.' },
    { key: '겨울 브라이트', dot: '#CC3355', bg: '#FCE4EC', desc: '선명하고 청량한 아이시 컬러.' },
    { key: '겨울 딥', dot: '#334466', bg: '#D1C4E9', desc: '짙은 네이비와 블랙.' },
    { key: '겨울 쿨', dot: '#6688AA', bg: '#C5CAE9', desc: '차가운 핑크와 라일락.' }
  ];

  const DIAG_Q1 = [
    {
      text: '손목 안쪽을 봤을 때, 혈관이 어떤 색으로 보여?',
      opts: [
        { key: 'W', label: '초록색이나 올리브색 🌿', desc: '웜톤 가능성' },
        { key: 'C', label: '파란색이나 보라색 💙', desc: '쿨톤 가능성' }
      ]
    },
    {
      text: '햇볕 아래에서 오랫동안 놀고 나면?',
      opts: [
        { key: 'W', label: '어둡게 잘 타는 편 🌅', desc: '웜톤 특징' },
        { key: 'C', label: '빨갛게 익는 편 🌹', desc: '쿨톤 특징' }
      ]
    }
  ];

  const DIAG_WARM_OPTS = [
    { key: '봄 라이트', desc: '밝고 화사한 색' },
    { key: '봄 브라이트', desc: '쨍하고 생생한 색' },
    { key: '봄 웜', desc: '따뜻하고 깊은 색' },
    { key: '가을 뮤트', desc: '차분하고 편안한 색' },
    { key: '가을 딥', desc: '깊고 어두운 색' },
    { key: '가을 웜', desc: '따뜻하고 성숙한 색' }
  ];

  const DIAG_COOL_OPTS = [
    { key: '여름 라이트', desc: '맑고 연한 색' },
    { key: '여름 뮤트', desc: '은은하고 회색빛 색' },
    { key: '여름 쿨', desc: '시원하고 청량한 색' },
    { key: '겨울 브라이트', desc: '눈에 확 띄는 진한 색' },
    { key: '겨울 딥', desc: '아주 어둡고 묵직한 색' },
    { key: '겨울 쿨', desc: '차갑고 선명한 색' }
  ];

  const SQ = [
    { text: '새로운 사람을 만나는 날, 거울 앞의 나는?', opts: [
      { key: 'A', text: '깔끔하고 단정하게! 지적이면서 세련된 인상 주고 싶어 ✨', sc: ['소피스티케이티드', '모던/미니멀', '매니시'] },
      { key: 'B', text: '부드럽고 편안하게! 금방 친해지고 싶은 사람처럼 보이고 싶어 ✌️', sc: ['캐주얼', '로맨틱', '페미닌'] }
    ] },
    { text: '온라인 쇼핑 중 더 눈길이 가는 옷은?', opts: [
      { key: 'A', text: '오래 입을 수 있는 기본템, 군더더기 없는 실루엣, 담백한 색감', sc: ['모던/미니멀', '캐주얼', '소피스티케이티드'] },
      { key: 'B', text: '한눈에 포인트가 보이는 아이템, 독특한 디테일, 눈에 띄는 분위기', sc: ['스트리트', '힙스터/펑크', '레트로/빈티지'] }
    ] },
    { text: '배가 살짝 부른 상태! 지금 내 옷의 핏은?', opts: [
      { key: 'A', text: '핏이 무너지면 안 되지! 딱 맞는 정사이즈로 📏', sc: [] },
      { key: 'B', text: '작은 것보단 큰 게 낫지! 넉넉하게 입는다 👕', sc: [] }
    ] },
    { text: '가장 기분 좋은 주말 외출은?', opts: [
      { key: 'A', text: '예쁜 카페에서 커피, 핫플에서 예쁜 사진 남기는 코스 📸', sc: ['페미닌', '로맨틱', '레트로/빈티지'] },
      { key: 'B', text: '산책, 피크닉, 돌아다니는 활동적인 코스', sc: ['스포티', '스트리트', '캐주얼'] }
    ] },
    { text: '오랜만의 문화생활! 더 끌리는 영화 포스터는?', opts: [
      { key: 'A', text: '차갑고 도시적인 장면, 절제된 톤, 시크한 주인공 🌃', sc: ['매니시', '모던/미니멀', '스트리트'] },
      { key: 'B', text: '빈티지한 햇살, 감성적인 장면, 로맨스 무드 ❤️', sc: ['로맨틱', '레트로/빈티지', '페미닌'] }
    ] },
    { text: '옷에서 좋아하는 포인트는?', opts: [
      { key: 'A', text: '로고나 패턴 없이 심플하고 색감이 깔끔한 기본템 🤍', sc: ['소피스티케이티드', '매니시', '모던/미니멀'] },
      { key: 'B', text: '흔하지 않은 디자인, 톡톡 튀는 컬러, 유니크한 포인트템 💖', sc: ['힙스터/펑크', '스트리트', '스포티'] }
    ] },
    { text: '더 편하게 느끼는 코디 방식은?', opts: [
      { key: 'A', text: '힘 빼고 자연스럽지만, 보기엔 센스 있는 꾸안꾸 스타일', sc: ['캐주얼', '스포티', '힙스터/펑크'] },
      { key: 'B', text: '무드가 분명하고, 분위기 자체가 예쁘게 완성되는 스타일', sc: ['페미닌', '로맨틱', '소피스티케이티드'] }
    ] },
    { text: '남들이 내 옷을 보고 해줬으면 하는 말은?', opts: [
      { key: 'A', text: '"와, 되게 멋있다. 자기 스타일 확실하다."', sc: ['매니시', '힙스터/펑크', '스트리트'] },
      { key: 'B', text: '"와, 분위기 있다. 되게 센스 있고 예쁘다."', sc: ['모던/미니멀', '레트로/빈티지', '스포티'] }
    ] },
    { text: '오늘 중요한 약속! 옷 고를 때 가장 먼저 드는 생각은?', opts: [
      { key: 'A', text: '어디서든 자연스럽게 어울리는 단정하고 무난한 스타일로', sc: ['소피스티케이티드', '모던/미니멀'] },
      { key: 'B', text: '사람들 만나는 자리니까 예쁘고 호감 가게 입고 싶어!', sc: ['페미닌', '로맨틱'] },
      { key: 'C', text: '격식 있는 자리니까 신경 써서 갖춰 입어야 해!', sc: ['소피스티케이티드', '매니시'] },
      { key: 'D', text: '오래 돌아다닐 거니까 편하고 활동성 있게 입자!', sc: ['스포티', '캐주얼'] }
    ] }
  ];

  const PERSONA_KEYS = ['소피스티케이티드', '페미닌', '힙스터/펑크', '캐주얼', '모던/미니멀', '로맨틱', '매니시', '스트리트', '스포티', '레트로/빈티지'];

  const state = {
    gender: null,
    personalColor: null,
    diagWarmCool: [],
    diagQ1Step: 0,
    surveyAnswers: {},
    currentQ: 0
  };

  function loadStoredState() {
    const appState = utils.getAppState();
    state.gender = appState.gender;
    state.personalColor = appState.personalColor;
    state.surveyAnswers = appState.surveyAnswers || {};
    state.currentQ = 0;
  }

  function persistState(extra) {
    utils.setAppState(Object.assign({
      gender: state.gender,
      personalColor: state.personalColor,
      surveyAnswers: state.surveyAnswers
    }, extra || {}));
  }

  function selectGender(gender) {
    state.gender = gender;
    persistState();
    ['W', 'M'].forEach(function (code) {
      const element = document.getElementById('gc-' + code);
      if (!element) return;
      const selected = code === gender;
      element.style.background = selected ? '#FFD93D' : '#D8D0FF';
      element.style.borderColor = selected ? '#C94F80' : '#1E1B3A';
      element.style.boxShadow = selected ? '3px 3px 0 #C94F80' : '5px 5px 0 #1E1B3A';
    });
  }

  function nextFromGender() {
    if (!state.gender) {
      utils.showAlert('성별을 선택해주세요!');
      return;
    }
    utils.goToScreen('s-color');
  }

  function buildColorGrid() {
    const grid = document.getElementById('color-grid');
    if (!grid) return;
    grid.innerHTML = '';
    COLORS.forEach(function (color) {
      const chip = document.createElement('div');
      chip.dataset.chip = color.key;
      chip.style.cssText = 'background:' + color.bg + ';border:2.5px solid #1E1B3A;border-radius:12px;padding:10px 6px;text-align:center;cursor:pointer;font-family:\'Jua\',sans-serif;font-size:12px;color:#1E1B3A;box-shadow:3px 3px 0 #1E1B3A;';
      chip.innerHTML = '<div style="width:28px;height:28px;border-radius:50%;border:2px solid #1E1B3A;margin:0 auto 5px;background:' + color.dot + '"></div>' +
        '<div>' + color.key + '</div>' +
        '<div style="font-size:10px;color:#7C6F9A;margin-top:2px;font-family:\'Noto Sans KR\',sans-serif;">' + color.desc + '</div>';
      chip.addEventListener('click', function () {
        selectColor(color.key);
      });
      grid.appendChild(chip);
    });
  }

  function selectColor(colorKey) {
    state.personalColor = colorKey;
    persistState();
    utils.$all('[data-chip]').forEach(function (chip) {
      const selected = chip.dataset.chip === colorKey;
      chip.style.outline = selected ? '3px solid #C94F80' : 'none';
      chip.style.transform = selected ? 'translate(3px,3px)' : 'none';
      chip.style.boxShadow = selected ? '0 0 0 #1E1B3A' : '3px 3px 0 #1E1B3A';
    });
  }

  function nextFromColor() {
    if (!state.personalColor) {
      utils.showAlert('퍼스널컬러를 선택해주세요!');
      return;
    }
    utils.navigate('survey.html');
  }

  function startDiag() {
    state.diagWarmCool = [];
    state.diagQ1Step = 0;
    renderDiag1();
    utils.goToScreen('s-diag-1');
  }

  function renderDiag1() {
    const question = DIAG_Q1[state.diagQ1Step];
    utils.$('#diag1-content').innerHTML =
      '<div style="font-size:13px;color:#7C6F9A;margin-bottom:8px;">질문 ' + (state.diagQ1Step + 1) + ' / 2</div>' +
      '<div style="font-size:18px;color:#1E1B3A;margin-bottom:16px;">' + question.text + '</div>' +
      '<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">' +
        question.opts.map(function (option) {
          return '<div class="diag1-option" data-key="' + option.key + '" style="background:#D8D0FF;border:3px solid #1E1B3A;border-radius:14px;padding:16px 10px;text-align:center;cursor:pointer;font-family:\'Jua\',sans-serif;font-size:15px;color:#1E1B3A;box-shadow:4px 4px 0 #1E1B3A;">' +
            '<div style="font-size:15px;font-weight:700;">' + option.label + '</div>' +
            '<div style="font-size:12px;color:#7C6F9A;margin-top:6px;">' + option.desc + '</div>' +
          '</div>';
        }).join('') +
      '</div>';

    utils.$all('.diag1-option').forEach(function (option) {
      option.addEventListener('click', function () {
        selectDiag1(option.dataset.key);
      });
    });
  }

  function selectDiag1(answerKey) {
    state.diagWarmCool.push(answerKey);
    if (state.diagQ1Step < DIAG_Q1.length - 1) {
      state.diagQ1Step += 1;
      renderDiag1();
      return;
    }
    renderDiag2();
    utils.goToScreen('s-diag-2');
  }

  function renderDiag2() {
    const hasWarm = state.diagWarmCool.includes('W');
    const hasCool = state.diagWarmCool.includes('C');
    let options = [];
    if (hasWarm && !hasCool) options = DIAG_WARM_OPTS;
    else if (!hasWarm && hasCool) options = DIAG_COOL_OPTS;
    else options = DIAG_WARM_OPTS.concat(DIAG_COOL_OPTS);

    utils.$('#diag2-content').innerHTML =
      '<div style="margin-bottom:14px;font-size:14px;color:#7C6F9A;font-family:\'Noto Sans KR\',sans-serif;">' +
        '1단계 결과: ' + (hasWarm && hasCool ? '웜/쿨 혼합형 🎨' : (hasWarm ? '웜톤 🌅' : '쿨톤 💙')) + '<br>' +
        '아래 중 지금 내 피부에 가장 잘 어울리는 느낌을 골라봐!' +
      '</div>' +
      '<div style="display:flex;flex-direction:column;gap:10px;">' +
        options.map(function (option) {
          const color = COLORS.find(function (entry) { return entry.key === option.key; });
          return '<div class="diag2-option" data-key="' + option.key + '" style="background:#D8D0FF;border:2.5px solid #1E1B3A;border-radius:13px;padding:12px 16px;cursor:pointer;font-family:\'Jua\',sans-serif;font-size:15px;color:#1E1B3A;box-shadow:4px 4px 0 #1E1B3A;display:flex;align-items:center;gap:12px;">' +
            '<div style="width:28px;height:28px;border-radius:50%;border:2px solid #1E1B3A;flex-shrink:0;background:' + (color ? color.dot : '#ccc') + ';"></div>' +
            '<div><div style="font-weight:700;">' + option.key + '</div><div style="font-size:12px;color:#7C6F9A;margin-top:2px;font-family:\'Noto Sans KR\',sans-serif;">' + option.desc + '</div></div>' +
          '</div>';
        }).join('') +
      '</div>';

    utils.$all('.diag2-option').forEach(function (option) {
      option.addEventListener('click', function () {
        selectDiag2(option.dataset.key);
      });
    });
  }

  function selectDiag2(colorKey) {
    state.personalColor = colorKey;
    persistState();
    utils.showAlert('진단 완료! 당신은 ' + colorKey + ' 타입이에요 🎨');
    utils.navigate('survey.html');
  }

  function renderSurvey() {
    const question = SQ[state.currentQ];
    const savedAnswer = state.surveyAnswers[state.currentQ];
    const progress = Math.round(((state.currentQ + 1) / SQ.length) * 100);

    utils.$('#q-prog-txt').textContent = 'Q' + (state.currentQ + 1) + ' / ' + SQ.length;
    utils.$('#q-prog-pct').textContent = progress + '%';
    utils.$('#pbar').style.width = progress + '%';
    utils.$('#q-num').textContent = 'Q' + (state.currentQ + 1);
    utils.$('#q-text').textContent = question.text;
    utils.$('#q-options').innerHTML = question.opts.map(function (option) {
      const selected = savedAnswer === option.key;
      return '<button class="survey-option" data-key="' + option.key + '" style="display:flex;align-items:flex-start;gap:12px;width:100%;padding:14px 16px;font-family:\'Jua\',sans-serif;font-size:16px;background:' + (selected ? '#FFD93D' : '#D8D0FF') + ';color:#1E1B3A;border:' + (selected ? '3' : '2.5') + 'px solid #1E1B3A;border-radius:13px;box-shadow:' + (selected ? '2px 2px' : '4px 4px') + ' 0 #1E1B3A;cursor:pointer;text-align:left;transform:' + (selected ? 'translate(2px,2px)' : 'none') + ';">' +
        '<span style="width:28px;height:28px;border-radius:50%;background:' + (selected ? '#C94F80' : '#1E1B3A') + ';color:#fff;display:flex;align-items:center;justify-content:center;font-size:15px;flex-shrink:0;">' + option.key + '</span>' +
        '<span style="flex:1;">' + option.text + '</span>' +
        (selected ? '<span style="flex-shrink:0;font-size:13px;background:#FF7BAC;color:#fff;border:2px solid #1E1B3A;border-radius:99px;padding:2px 10px;align-self:center;">✔ 선택</span>' : '') +
      '</button>';
    }).join('');

    utils.$all('.survey-option').forEach(function (button) {
      button.addEventListener('click', function () {
        selectAnswer(button.dataset.key);
      });
    });

    utils.$('#survey-next-btn').textContent = state.currentQ === SQ.length - 1 ? '결과 보기 🎉' : '다음 →';
    persistState();
  }

  function selectAnswer(answerKey) {
    state.surveyAnswers[state.currentQ] = answerKey;
    renderSurvey();
  }

  function surveyPrev() {
    if (state.currentQ === 0) {
      utils.navigate('index.html');
      return;
    }
    state.currentQ -= 1;
    renderSurvey();
  }

  function surveyNext() {
    if (!state.surveyAnswers[state.currentQ]) {
      utils.showAlert('선택해주세요!');
      return;
    }

    if (state.currentQ < SQ.length - 1) {
      state.currentQ += 1;
      renderSurvey();
      return;
    }

    startLoading();
  }

  function calcResultFromAnswers(answers) {
    const scores = {};
    PERSONA_KEYS.forEach(function (key) {
      scores[key] = 0;
    });

    SQ.forEach(function (question, index) {
      const answer = answers[index];
      if (!answer) return;
      const matched = question.opts.find(function (option) { return option.key === answer; });
      if (!matched || !matched.sc) return;
      matched.sc.forEach(function (persona) {
        if (persona in scores) scores[persona] += 1;
      });
    });

    return Object.entries(scores).sort(function (left, right) {
      return right[1] - left[1];
    })[0][0];
  }

  function setLoadingMessage(message) {
    const target = utils.$('#loading-msg');
    if (target) target.textContent = message;
  }

  async function submitSurveyFlow(localResultType) {
    const surveyState = {
      gender: state.gender,
      personalColor: state.personalColor,
      surveyAnswers: state.surveyAnswers,
      resultType: localResultType
    };

    const surveyMeta = {
      completedAt: new Date().toISOString(),
      usedMockFallback: false,
      apiStatus: 'pending'
    };

    let profileResponse = null;
    let recommendationResponse = null;
    let resolvedResultType = localResultType;

    try {
      setLoadingMessage('프로필 분석 요청 중...');
      profileResponse = await api.fetchProfileFromState(surveyState);
      resolvedResultType = api.extractResultType(profileResponse) || api.extractResultType(api.extractProfileData(profileResponse)) || localResultType;
      surveyMeta.apiStatus = 'profile-ok';
    } catch (profileError) {
      surveyMeta.apiStatus = 'profile-failed';
      surveyMeta.profileError = profileError.message;
    }

    try {
      setLoadingMessage('추천 상품 요청 중...');
      recommendationResponse = await api.fetchRecommendationsFromState(
        Object.assign({}, surveyState, { resultType: resolvedResultType }),
        profileResponse,
        { topN: 5 }
      );
      const normalized = api.normalizeRecommendationResponse(recommendationResponse);
      resolvedResultType = normalized.resultType || resolvedResultType;
      surveyMeta.apiStatus = surveyMeta.apiStatus === 'profile-ok' ? 'ok' : 'recommendation-only';
    } catch (recommendationError) {
      surveyMeta.recommendationError = recommendationError.message;
      surveyMeta.usedMockFallback = true;
      if (surveyMeta.apiStatus === 'profile-ok') {
        surveyMeta.apiStatus = 'recommendation-failed';
      }
    }

    persistState({
      resultType: resolvedResultType,
      surveyAnswers: state.surveyAnswers,
      surveyMeta: surveyMeta,
      profileResponse: profileResponse,
      recommendationResponse: recommendationResponse
    });

    utils.navigate('result.html');
  }

  function startLoading() {
    utils.goToScreen('s-loading');
    const messages = [
      '퍼스널컬러 데이터 연산 중...',
      '스타일 DNA 분석 중...',
      '맞춤 페르소나 매칭 중...',
      'FastAPI /profile 호출 준비 중...',
      'FastAPI /recommendations 호출 준비 중...'
    ];

    let index = 0;
    setLoadingMessage(messages[0]);
    const interval = window.setInterval(function () {
      setLoadingMessage(messages[index % messages.length]);
      index += 1;
    }, 650);

    const resultType = calcResultFromAnswers(state.surveyAnswers);
    submitSurveyFlow(resultType)
      .catch(function (error) {
        persistState({
          resultType: resultType,
          surveyMeta: {
            completedAt: new Date().toISOString(),
            apiStatus: 'failed',
            usedMockFallback: true,
            fatalError: error.message
          },
          profileResponse: null,
          recommendationResponse: null
        });
        utils.navigate('result.html');
      })
      .finally(function () {
        window.clearInterval(interval);
      });
  }

  function initIndexPage() {
    loadStoredState();
    buildColorGrid();

    utils.$('#start-button').addEventListener('click', function () {
      utils.goToScreen('s-gender');
    });
    utils.$('#gc-W').addEventListener('click', function () { selectGender('W'); });
    utils.$('#gc-M').addEventListener('click', function () { selectGender('M'); });
    utils.$('#gender-next-btn').addEventListener('click', nextFromGender);
    utils.$('#open-color-select-btn').addEventListener('click', function () { utils.goToScreen('s-color-select'); });
    utils.$('#start-diag-btn').addEventListener('click', startDiag);
    utils.$('#color-next-btn').addEventListener('click', nextFromColor);
    utils.$('#color-back-btn').addEventListener('click', function () { utils.goToScreen('s-color'); });
    utils.$('#diag1-back-btn').addEventListener('click', function () { utils.goToScreen('s-color'); });
    utils.$('#diag2-back-btn').addEventListener('click', function () { utils.goToScreen('s-diag-1'); });

    if (state.gender) selectGender(state.gender);
    if (state.personalColor) selectColor(state.personalColor);
  }

  function initSurveyPage() {
    loadStoredState();
    if (!state.gender) {
      utils.navigate('index.html');
      return;
    }

    utils.buildSpinner('spinner');
    utils.$('#survey-prev-btn').addEventListener('click', surveyPrev);
    utils.$('#survey-next-btn').addEventListener('click', surveyNext);
    renderSurvey();
  }

  document.addEventListener('DOMContentLoaded', function () {
    const page = document.body.dataset.page;
    if (page === 'index') initIndexPage();
    if (page === 'survey') initSurveyPage();
  });

  window.MapsiSurvey = {
    initIndexPage: initIndexPage,
    initSurveyPage: initSurveyPage,
    calcResultFromAnswers: calcResultFromAnswers
  };
})(window);
