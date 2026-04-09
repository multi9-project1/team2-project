(function (window) {
  const utils = window.MapsiUtils;
  const api = window.MapsiApi || {};

  const COLOR_GUIDE = {
    '봄 라이트': { ms: ['화이트', '아이보리', '라이트핑크', '피치', '코럴', '옐로우'], zz: ['화이트', '아이보리', '라이트핑크', '피치'] },
    '봄 브라이트': { ms: ['핑크', '오렌지', '레드', '민트', '그린', '옐로우'], zz: ['핑크', '오렌지', '레드', '민트'] },
    '봄 웜': { ms: ['아이보리', '베이지', '오렌지', '머스타드', '샌드'], zz: ['아이보리', '베이지', '브라운', '오렌지'] },
    '여름 라이트': { ms: ['화이트', '라이트핑크', '스카이블루', '라벤더'], zz: ['화이트', '라이트핑크', '라이트블루', '퍼플'] },
    '여름 뮤트': { ms: ['그레이', '라이트그레이', '다크그레이', '블루'], zz: ['그레이', '챠콜', '로즈', '모브', '블루'] },
    '여름 쿨': { ms: ['화이트', '블루', '네이비', '실버'], zz: ['화이트', '블루', '네이비', '실버'] },
    '가을 뮤트': { ms: ['베이지', '다크베이지', '카키', '오트밀'], zz: ['베이지', '카키', '민트', '브라운'] },
    '가을 딥': { ms: ['다크브라운', '딥레드', '버건디', '진청'], zz: ['브라운', '버건디', '챠콜'] },
    '가을 웜': { ms: ['카멜', '머스타드', '다크오렌지', '브라운'], zz: ['오렌지', '브라운', '카키', '골드'] },
    '겨울 브라이트': { ms: ['블랙', '화이트', '레드', '블루', '퍼플'], zz: ['블랙', '화이트', '레드', '블루', '퍼플'] },
    '겨울 딥': { ms: ['블랙', '다크네이비', '다크그린', '버건디'], zz: ['블랙', '네이비', '버건디', '챠콜'] },
    '겨울 쿨': { ms: ['화이트', '네이비', '실버', '데님'], zz: ['화이트', '네이비', '실버'] }
  };

  const CAT_FITS = {
    '상의': ['슬림핏', '루즈핏', '오버핏', '크롭핏', '박시핏', '레귤러핏'],
    '아우터': ['오버핏', '루즈핏', '슬림핏', '크롭핏', '롱라인', '벨티드'],
    '팬츠': ['와이드핏', '슬림핏', '스트레이트핏', '부츠컷', '조거핏', '테이퍼드핏', '하이웨스트'],
    '원피스': ['A라인', 'H라인', '플레어', '머메이드', '슬림핏', '루즈핏', '랩핏', '셔츠핏'],
    '니트/카디건': ['루즈핏', '슬림핏', '오버핏', '크롭핏', '레귤러핏'],
    '스커트': ['A라인', 'H라인', '플레어', '머메이드', '타이트핏', '랩핏', '플리츠'],
    '트레이닝': ['루즈핏', '오버핏', '조거핏', '세미슬림']
  };

  const STYLE_FIT_MAP = {
    '소피스티케이티드': ['슬림핏', '레귤러핏', 'H라인'],
    '페미닌': ['슬림핏', 'A라인', '랩핏', '플레어'],
    '힙스터/펑크': ['오버핏', '타이트핏', '크롭핏', '와이드핏'],
    '캐주얼': ['레귤러핏', '스트레이트핏', '세미슬림'],
    '모던/미니멀': ['레귤러핏', '슬림핏', '스트레이트핏'],
    '로맨틱': ['A라인', '플레어', '크롭핏'],
    '매니시': ['레귤러핏', '루즈핏', '스트레이트핏'],
    '스트리트': ['오버핏', '루즈핏', '박시핏', '와이드핏'],
    '스포티': ['조거핏', '루즈핏', '트레이닝핏'],
    '레트로/빈티지': ['부츠컷', '테이퍼드핏', '롱라인']
  };

  const PERSONAS = {
    '소피스티케이티드': { icon: '💻', imgFile: 'sophisticated', tF: '갓생 사는 도심 속 차도녀', tM: '갓생 사는 도심 속 차도남', q: '"8시 55분, 아아 한 잔과 함께 업무 모드 ON!"', d: '아침 이슬 머금은 셔츠처럼 언제나 흐트러짐 없는 당신! 복잡한 도심 속에서도 나만의 칼각과 리듬을 지키는 프로페셔널한 타입이에요.', items: ['잘 다려진 셔츠', '핏이 딱 떨어지는 슬랙스', '툭 걸쳐도 멋진 블레이저 🧥'], pt: '단정하고 정돈된 느낌이 당신의 지적인 분위기를 200% 살려줄 거예요! ✨', tip: '블레이저와 슬랙스 조합으로 갓생 오피스룩을 완성해봐. 발색 좋은 단색 아이템 위주로 레이어드하면 더욱 세련돼 보여!', eF: '👩‍💼', eM: '👨‍💼', bg: '#EEF2FF' },
    '페미닌': { icon: '🌸', imgFile: 'feminine', tF: '호수 위의 백조, 우아함 한 스푼 여신', tM: '호수 위의 백조, 우아함 한 스푼', q: '"은은하게 퍼지는 샴푸 향기처럼 몽글몽글하게"', d: '화사하게 피어난 꽃처럼 언제나 부드럽고 우아한 선을 사랑하는 당신!', items: ['라인을 살려주는 원피스', '하늘하늘한 블라우스', '페미닌한 무드의 스커트 🦢'], pt: '부드럽고 여성스러운 디테일이 당신의 우아한 이미지를 더욱 빛나게 해줄 거예요! ✨', tip: '플로럴 패턴이나 레이스 디테일로 포인트를 주면 더욱 화사해져. 드레이프가 자연스럽게 흐르는 소재를 선택해봐!', eF: '🧝‍♀️', eM: '🧝', bg: '#FFF0F5' },
    '힙스터/펑크': { icon: '🎸', imgFile: 'hipster_punk', tF: '톡톡 튀는 인간 팝핑캔디', tM: '톡톡 튀는 인간 팝핑캔디', q: '"톡 쏘는 탄산처럼 강렬한 존재감"', d: '평범한 건 거부한다! 독특하고 화려한 스타일로 자신을 표현할 줄 아는 용감한 타입.', items: ['화려한 패턴의 상의', '독특한 워싱의 데님', '시선 강탈 포인트 액세서리 💖'], pt: '화려하고 독특한 개성이 당신의 힙한 감성을 200% 완성해 줄 거예요! 😎', tip: '믹스앤매치가 포인트! 서로 다른 패턴끼리 과감하게 레이어드하고, 빈티지 액세서리로 개성을 살려봐.', eF: '🧑‍🎤', eM: '🧑‍🎤', bg: '#FFF8E1' },
    '캐주얼': { icon: '🎒', imgFile: 'casual', tF: '어디서나 찰떡! 호불호 제로 카멜레온', tM: '어디서나 찰떡! 호불호 제로 카멜레온', q: '"무심한 듯 툭 걸친 티셔츠 한 장으로 완벽한 밸런스"', d: '어떤 모임에 가도 편안하게 스며드는 친근한 매력! 실용적이면서도 깔끔한 꾸안꾸 정석.', items: ['편안한 맨투맨', '활동성 좋은 데님 팬츠', '가벼운 캔버스화 👟'], pt: '실용적이고 깔끔한 느낌이 당신의 맑고 깨끗한 분위기를 200% 살려줄 거예요! ✨', tip: '기본 아이템 퀄리티에 투자해봐. 좋은 소재의 화이트 티셔츠 하나로도 완성도 높은 꾸안꾸 연출이 가능해!', eF: '🧑', eM: '🧑', bg: '#F0FFF4' },
    '모던/미니멀': { icon: '🧊', imgFile: 'modern_minimal', tF: '군더더기 제로, 시크한 얼음물 한 잔', tM: '군더더기 제로, 시크한 얼음물 한 잔', q: '"비움의 미학을 아는 차분한 아우라"', d: '복잡한 건 딱 질색! 깔끔한 선과 무채색의 조화로운 무드를 즐기는 냉철한 감각가.', items: ['무채색 코트나 재킷', '로고 없는 니트', '딱 떨어지는 슬랙스 🧥'], pt: '깔끔하고 무난한 핏이 오히려 당신의 감각적인 카리스마를 더욱 돋보이게 해줄 거예요! 🧊', tip: '컬러 팔레트를 블랙-화이트-그레이 3색으로 제한해봐. 소재와 실루엣의 차이만으로도 풍성한 레이어드가 완성돼!', eF: '🧑‍💻', eM: '🧑‍💻', bg: '#F5F5F5' },
    '로맨틱': { icon: '🎀', imgFile: 'romantic', tF: '인간 벚꽃 솜사탕, 사랑스러움의 결정체', tM: '인간 벚꽃 솜사탕, 사랑스러움의 결정체', q: '"바라만 봐도 기분이 좋아지는 따뜻한 봄 햇살"', d: '포근하고 다정한 마음씨만큼이나 사랑스러운 스타일을 추구하는 로맨티스트!', items: ['파스텔 톤 가디건', '리본 디테일 블라우스', '부드러운 니트 아이템 🌸'], pt: '부드럽고 발랄한 무드가 당신의 사랑스러운 매력을 200% 폭발시켜줄 거예요! 💖', tip: '리본이나 레이스 같은 여성스러운 디테일을 포인트로 활용해봐. 파스텔 컬러 코디에 골드 액세서리면 금상첨화!', eF: '🌸', eM: '🌸', bg: '#FFF0F5' },
    '매니시': { icon: '🕴️', imgFile: 'mannish', tF: '무심한 듯 툭, 시크한 선배미 뿜뿜', tM: '무심한 듯 툭, 시크한 선배미 뿜뿜', q: '"묵직한 울림, 중성적인 매력에 자꾸만 눈길이"', d: '도시적이고 멋진 이미지를 선호하며, 자신만의 뚜렷한 주관을 스타일로 표현할 줄 알아요.', items: ['오버핏 자켓', '와이드 슬랙스', '클래식한 옥스포드화 👞'], pt: '도시적이면서도 멋있는 분위기가 당신의 쿨한 멋을 200% 완성해 줄 거예요! 😎', tip: '오버사이즈 남성복 아이템을 여성스러운 요소와 믹스해봐. 와이드 팬츠에 크롭 아이템 조합이 비율 맛집이야!', eF: '🧥', eM: '🧥', bg: '#F3F4F6' },
    '스트리트': { icon: '🛹', imgFile: 'street', tF: '뒷골목 런웨이, 자유로운 영혼의 지배자', tM: '뒷골목 런웨이, 자유로운 영혼의 지배자', q: '"정해진 틀을 깨부수는 거리의 주인공"', d: '어디로 튈지 모르는 자유로운 에너지와 트렌디한 감각이 공존하는 당신!', items: ['편안한 후드티', '넉넉한 카고 팬츠', '트렌디한 조거 팬츠 🎧'], pt: '활동적이고 트렌디한 무드가 당신의 자유로운 영혼을 200% 보여줄 거예요! 🛹', tip: '그래픽 로고 아이템에 카고 팬츠 조합이 스트리트 핵심! 캡모자나 비니로 힙한 포인트를 더해봐.', eF: '🛹', eM: '🛹', bg: '#EFF6FF' },
    '스포티': { icon: '🏃', imgFile: 'sporty', tF: '에너지 1000%, 지치지 않는 인간 비타민', tM: '에너지 1000%, 지치지 않는 인간 비타민', q: '"존재만으로도 주변을 환하게 밝히는 에너자이저"', d: '건강한 에너지와 활동적인 스타일이 당신의 가장 큰 매력 포인트!', items: ['아노락 자켓', '레깅스나 트레이닝 셋업', '야구 모자 🧢'], pt: '활동적이고 편안한 핏이 당신의 건강한 이미지를 200% 완성해 줄 거예요! ⚡', tip: '스포츠 브랜드 셋업에 슬리퍼나 샌들 조합이 요즘 트렌디한 스포티룩이야. 컬러블록으로 생동감을 더해봐!', eF: '🏃‍♀️', eM: '🏃', bg: '#ECFDF5' },
    '레트로/빈티지': { icon: '📻', imgFile: 'retro', tF: '낭만 가득한 시간여행자', tM: '낭만 가득한 시간여행자', q: '"아날로그 필름 카메라 속에 담긴 따뜻한 기록"', d: '남들은 모르는 독특한 색감과 과거의 낭만을 찾아 여행하는 아날로그 감성가!', items: ['체크무늬 셔츠', '코듀로이 팬츠', '빛바랜 그래픽 티셔츠 🎞️'], pt: '독특하고 트렌디한 빈티지 감성이 당신의 깊은 매력을 200% 담아내 줄 거예요! 📻', tip: '구제샵이나 빈티지샵에서 90-00년대 아이템 발굴해봐. 부츠컷 데님과 빈티지 가죽 자켓 조합은 레트로룩의 기본!', eF: '📷', eM: '📷', bg: '#FDF6EC' }
  };

  const state = {
    gender: null,
    personalColor: null,
    resultType: null,
    selectedCat: '상의',
    profileResponse: null,
    recommendationResponse: null,
    surveyMeta: {}
  };

  function loadState() {
    const appState = utils.getAppState();
    state.gender = appState.gender;
    state.personalColor = appState.personalColor;
    state.resultType = appState.resultType;
    state.profileResponse = appState.profileResponse;
    state.recommendationResponse = appState.recommendationResponse;
    state.surveyMeta = appState.surveyMeta || {};
  }

  function getPersona() {
    return PERSONAS[state.resultType] || PERSONAS['캐주얼'];
  }

  function renderStatusMessage() {
    if (!state.surveyMeta || !state.surveyMeta.apiStatus || state.surveyMeta.apiStatus === 'ok') return;
    const container = document.createElement('div');
    container.style.cssText = 'background:#FFF8E1;border:3px solid #1E1B3A;border-radius:14px;padding:12px 14px;margin-bottom:16px;box-shadow:4px 4px 0 #1E1B3A;font-family:\'Noto Sans KR\',sans-serif;font-size:14px;line-height:1.6;color:#1E1B3A;';
    let message = '일부 API 응답을 해석하지 못해 기본 결과 UI를 사용 중입니다.';
    if (state.surveyMeta.apiStatus === 'profile-failed') message = '/profile 호출에 실패해 프론트 계산 결과로 표시 중입니다.';
    if (state.surveyMeta.apiStatus === 'recommendation-failed') message = '/recommendations 호출에 실패해 결과 카드만 먼저 표시 중입니다.';
    if (state.surveyMeta.apiStatus === 'failed') message = '백엔드 응답을 가져오지 못해 기본 결과 UI를 표시 중입니다.';
    container.textContent = message;
    const app = utils.$('.app');
    if (app) app.insertBefore(container, app.firstChild.nextSibling);
  }

  function buildFallbackAnalysisSummary() {
    const analysis = (state.recommendationResponse && state.recommendationResponse.preference_analysis) || {};
    const profile = (state.recommendationResponse && state.recommendationResponse.user_profile) || (state.profileResponse && state.profileResponse.user_profile) || {};
    const genderMap = { M: '남성', W: '여성', U: '공용' };
    const fitMap = { T: ['노멀 핏', '타이트 핏'], L: ['루즈 핏', '노멀 핏'] };
    const eraLabel = analysis.era_label || (analysis.era ? String(analysis.era) + '년대' : '취향 분석 기준');
    const styleLabel = analysis.style || state.resultType || '캐주얼';
    const similarity = analysis.similarity_percent || 0;
    const fitLabels = fitMap[profile.fit_preference] || ['노멀 핏'];
    return {
      title: '분석 요약',
      description: '알고리즘 분석 결과, 당신의 취향은 [' + eraLabel + ' | ' + styleLabel + ']와 ' + similarity + '% 일치합니다.',
      chips: [
        { key: 'gender', label: '성별', value: genderMap[state.gender || profile.gender] || '공용' },
        { key: 'personal_color', label: '퍼스널컬러', value: state.personalColor || profile.personal_color_display || '모르겠음' },
        { key: 'fit', label: '핏', value: fitLabels.join(' / ') }
      ]
    };
  }

  function renderAnalysisSummary() {
    const card = utils.$('#analysis-summary-card');
    const titleEl = utils.$('#analysis-summary-title');
    const textEl = utils.$('#analysis-summary-text');
    const tagsEl = utils.$('#analysis-summary-tags');
    if (!card || !titleEl || !textEl || !tagsEl) return;

    const summary = (state.recommendationResponse && state.recommendationResponse.analysis_summary) || buildFallbackAnalysisSummary();
    if (!summary) return;

    titleEl.textContent = summary.title || '분석 요약';
    textEl.innerHTML = utils.escapeHtml(summary.description || '').replace(/\[(.*?)\]/g, '<strong>[$1]</strong>').replace(/(\d+%)/g, '<strong>$1</strong>');

    const chips = Array.isArray(summary.chips) ? summary.chips : [];
    tagsEl.innerHTML = chips.map(function (chip) {
      return '<span class="analysis-chip">' + utils.escapeHtml(chip.label || '') + ': ' + utils.escapeHtml(chip.value || '') + '</span>';
    }).join('');

    card.style.display = 'block';
  }

  function renderResult() {
    const persona = getPersona();
    const isFemale = state.gender === 'W';

    utils.$('#result-badge').textContent = '나의 맵시TI: ' + persona.icon + ' ' + state.resultType;
    var imgSuffix = isFemale ? '_w' : '_m';
    var imgSrc = 'assets/images/' + persona.imgFile + imgSuffix + '.png';
    utils.$('#char-img').innerHTML = '<img src="' + imgSrc + '" alt="' + utils.escapeHtml(state.resultType) + '" style="width:100%;height:100%;object-fit:contain;border-radius:12px;">';
    utils.$('#result-char').style.background = persona.bg;
    utils.$('#result-title').textContent = persona.icon + ' ' + state.resultType;
    utils.$('#result-sub').textContent = isFemale ? persona.tF : persona.tM;

    utils.$('#result-desc-card').style.background = persona.bg;
    utils.$('#result-desc').innerHTML =
      '<div style="font-size:16px;color:#C94F80;margin-bottom:10px;">' + persona.q + '</div>' +
      '<div style="font-family:\'Noto Sans KR\',sans-serif;font-size:15px;line-height:1.8;color:#1E1B3A;">' + persona.d + '</div>' +
      '<div style="margin-top:12px;padding:12px;background:#fff;border-radius:12px;border:2px dashed #E2C9F0;font-size:15px;color:#C94F80;">✨ ' + persona.pt + '</div>';

    utils.$('#result-items').innerHTML =
      '<div style="margin-top:14px;font-size:17px;color:#1E1B3A;margin-bottom:6px;">당신의 최애 아이템 🛍️</div>' +
      persona.items.map(function (item) {
        return '<div style="font-size:15px;padding:7px 0;border-bottom:2px dashed #E2C9F0;color:#1E1B3A;font-family:\'Noto Sans KR\',sans-serif;">• ' + item + '</div>';
      }).join('');

    utils.$('#style-tip-card').style.background = persona.bg;
    utils.$('#style-tip-text').textContent = persona.tip;

    utils.$('#point-color-card').style.background = persona.bg;
    const guide = COLOR_GUIDE[state.personalColor] || { ms: ['블랙', '화이트', '그레이'], zz: ['블랙', '화이트', '그레이'] };
    const allColors = Array.from(new Set([].concat(guide.ms, guide.zz))).slice(0, 6);
    utils.$('#point-color-tags').innerHTML =
      '<div style="font-size:12px;color:#7C6F9A;margin-bottom:6px;font-family:\'Noto Sans KR\',sans-serif;">' + state.personalColor + ' 추천 컬러</div>' +
      allColors.map(function (color) {
        return '<span class="tag" style="background:#fff;color:#1E1B3A;">' + color + '</span>';
      }).join('');

    buildCategoryTabs();
    updateSelects();
  }

  function getCategories() {
    const categories = ['상의', '아우터', '팬츠', '니트/카디건'];
    if (state.gender === 'W') categories.push('원피스', '스커트', '트레이닝');
    else categories.push('트레이닝');
    return categories;
  }

  function buildCategoryTabs() {
    utils.$('#cat-tabs').innerHTML = getCategories().map(function (category) {
      const selected = category === state.selectedCat;
      return '<button class="cat-tab" data-cat="' + category + '" style="padding:8px 16px;font-family:\'Jua\',sans-serif;font-size:15px;background:' + (selected ? '#FF7BAC' : '#D8D0FF') + ';color:' + (selected ? '#fff' : '#1E1B3A') + ';border:2.5px solid #1E1B3A;border-radius:99px;box-shadow:' + (selected ? '2px 2px' : '3px 3px') + ' 0 #1E1B3A;cursor:pointer;transform:' + (selected ? 'translate(1px,1px)' : 'none') + ';">' + category + '</button>';
    }).join('');

    utils.$all('.cat-tab').forEach(function (button) {
      button.addEventListener('click', function () {
        state.selectedCat = button.dataset.cat;
        buildCategoryTabs();
        updateSelects();
        utils.$('#product-results').innerHTML = '';
        utils.$('#shop-links').innerHTML = '';
      });
    });
  }

  function updateSelects() {
    const categoryFits = CAT_FITS[state.selectedCat] || ['레귤러핏', '루즈핏', '슬림핏'];
    const styleFits = STYLE_FIT_MAP[state.resultType] || [];
    const prioritizedFits = categoryFits.filter(function (fit) {
      return styleFits.some(function (mappedFit) { return fit.includes(mappedFit); });
    });
    const fitOptions = prioritizedFits.length > 0
      ? prioritizedFits.concat(categoryFits.filter(function (fit) { return !prioritizedFits.includes(fit); }))
      : categoryFits;

    utils.$('#fit-select').innerHTML = fitOptions.map(function (fit) {
      return '<option value="' + fit + '">' + fit + '</option>';
    }).join('');

    const guide = COLOR_GUIDE[state.personalColor] || { ms: ['블랙', '화이트', '그레이'] };
    utils.$('#color-select').innerHTML = guide.ms.map(function (color) {
      return '<option value="' + color + '">' + color + '</option>';
    }).join('');
  }

  function renderProductCards(title, items) {
    if (!items || !items.length) {
      return '<div style="font-size:15px;color:#7C6F9A;font-family:\'Noto Sans KR\',sans-serif;margin-bottom:12px;">' + title + ' 결과가 아직 없어요.</div>';
    }

    return '<div style="font-size:16px;color:#1E1B3A;margin-bottom:12px;font-weight:700;">' + title + '</div>' +
      items.map(function (item) {
        const imageHtml = item.imageUrl
          ? '<img src="' + utils.escapeHtml(item.imageUrl) + '" alt="' + utils.escapeHtml(item.name) + '" style="width:70px;height:80px;object-fit:cover;background:#fff;border-radius:8px;border:1.5px solid #E2C9F0;flex-shrink:0;">'
          : '<div style="width:70px;height:80px;background:#fff;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:26px;border:1.5px solid #E2C9F0;flex-shrink:0;">🛍️</div>';
        const titleHtml = item.productUrl
          ? '<a href="' + utils.escapeHtml(item.productUrl) + '" target="_blank" style="font-size:14px;color:#1E1B3A;margin:3px 0;line-height:1.4;font-family:\'Noto Sans KR\',sans-serif;text-decoration:none;">' + utils.escapeHtml(item.name) + '</a>'
          : '<div style="font-size:14px;color:#1E1B3A;margin:3px 0;line-height:1.4;font-family:\'Noto Sans KR\',sans-serif;">' + utils.escapeHtml(item.name) + '</div>';
        const reasonHtml = item.reason
          ? '<div style="font-size:12px;color:#7C6F9A;font-family:\'Noto Sans KR\',sans-serif;margin-top:4px;">' + utils.escapeHtml(item.reason) + '</div>'
          : '';
        return '<div style="display:flex;align-items:center;gap:12px;padding:12px;background:#F8FAFC;border:2px solid #1E1B3A;border-radius:12px;box-shadow:3px 3px 0 #1E1B3A;margin-bottom:10px;">' +
          imageHtml +
          '<div style="flex:1;">' +
            '<div style="font-size:12px;color:#7C6F9A;font-family:\'Noto Sans KR\',sans-serif;">' + utils.escapeHtml(item.brand || item.mall || '추천 상품') + '</div>' +
            titleHtml +
            '<div style="font-size:16px;color:#C94F80;font-weight:700;">' + utils.escapeHtml(utils.formatPrice(item.price) || '가격 정보 없음') + '</div>' +
            reasonHtml +
          '</div>' +
        '</div>';
      }).join('');
  }

  function renderProductsFromResponse(normalizedResponse, filters) {
    const results = [];
    if (normalizedResponse.musinsa.length) {
      results.push(renderProductCards('🛍️ 무신사 추천 상품', normalizedResponse.musinsa));
    }
    if (state.gender === 'W' && normalizedResponse.zigzag.length) {
      results.push('<div style="margin-top:16px;">' + renderProductCards('🛍️ 지그재그 추천 상품', normalizedResponse.zigzag) + '</div>');
    }
    if (!results.length && normalizedResponse.all.length) {
      results.push(renderProductCards('🛍️ 추천 상품', normalizedResponse.all));
    }
    if (!results.length) {
      results.push('<div style="font-size:14px;color:#7C6F9A;font-family:\'Noto Sans KR\',sans-serif;">백엔드에서 추천 상품을 아직 반환하지 않았어요. 아래 전체 보기 링크로 검색 결과를 확인해보세요.</div>');
    }
    utils.$('#product-results').innerHTML = results.join('');

    const derivedLinks = api.buildSearchLinks(filters);
    const links = normalizedResponse.links || {};
    let html = '<a href="' + utils.escapeHtml(links.musinsa || derivedLinks.musinsa) + '" target="_blank" style="flex:1;display:block;padding:12px;text-align:center;font-family:\'Jua\',sans-serif;font-size:15px;background:#1E1B3A;color:#fff;border:3px solid #1E1B3A;border-radius:12px;box-shadow:4px 4px 0 #A78BFA;text-decoration:none;">무신사 전체 보기 →</a>';
    if (state.gender === 'W') {
      html += '<a href="' + utils.escapeHtml(links.zigzag || derivedLinks.zigzag) + '" target="_blank" style="flex:1;display:block;padding:12px;text-align:center;font-family:\'Jua\',sans-serif;font-size:15px;background:#A78BFA;color:#fff;border:3px solid #1E1B3A;border-radius:12px;box-shadow:4px 4px 0 #1E1B3A;text-decoration:none;">지그재그 전체 보기 →</a>';
    }
    utils.$('#shop-links').innerHTML = html;
  }

  async function loadProducts() {
    const filters = {
      gender: state.gender,
      category: state.selectedCat,
      fit: (utils.$('#fit-select') && utils.$('#fit-select').value) || '레귤러핏',
      color: (utils.$('#color-select') && utils.$('#color-select').value) || '블랙'
    };
    const button = utils.$('#preview-btn');
    button.textContent = '⏳ 실시간 추출 중 (약 15초 소요)...';
    button.disabled = true;

    try {
      if (!window.MapsiApi || !window.MapsiApi.buildSurveyObject) {
        throw new Error('API 라이브러리가 아직 로드되지 않았습니다. 잠시 후 다시 시도해주세요.');
      }

      const survey = window.MapsiApi.buildSurveyObject(utils.getAppState());
      const payload = {
        survey: survey,
        category_name: filters.category,
        selected_color: filters.color,
        top_n: 3
      };

      // 1. 무신사 실시간 크롤링 호출
      const musinsaRes = await window.MapsiApi.request('/crawl/musinsa', {
        method: 'POST',
        body: JSON.stringify(payload)
      });

      // 2. 지그재그 실시간 크롤링 호출 (여성인 경우만)
      let zigzagRes = { items: [] };
      if (state.gender === 'W') {
        zigzagRes = await window.MapsiApi.request('/crawl/zigzag', {
          method: 'POST',
          body: JSON.stringify(payload)
        }).catch(() => ({ items: [] }));
      }

      const combined = {
        musinsa: musinsaRes.items || [],
        zigzag: zigzagRes.items || [],
        url: musinsaRes.url
      };

      const normalized = window.MapsiApi.normalizeRecommendationResponse(combined);
      renderProductsFromResponse(normalized, filters);
      
    } catch (error) {
      console.error('Crawler Error:', error);
      utils.showAlert('크롤링 실패: ' + error.message);
      // 실패 시 빈 결과 표시 (더미 대신)
      utils.$('#product-results').innerHTML = '<div style="padding:20px;text-align:center;color:#C94F80;">실시간 데이터를 가져오지 못했습니다.<br>잠시 후 다시 시도해 주세요.</div>';
    } finally {
      button.textContent = '⚡ 맞춤 상품 보기';
      button.disabled = false;
    }
  }

  function shareResult() {
    utils.showAlert('결과 카드 공유 기능은 실제 서비스에서 연동됩니다! 📸');
  }

  function resetAll() {
    utils.clearAppState();
    utils.navigate('index.html');
  }

  function initResultPage() {
    loadState();
    if (!state.gender || !state.resultType) {
      utils.navigate('index.html');
      return;
    }

    renderStatusMessage();
    renderResult();
    renderAnalysisSummary();

    // 결과 화면 진입 시에는 상품 영역을 비워 둡니다.
    // 사용자가 '맞춤 상품 보기' 버튼을 눌렀을 때만 실시간 상품을 렌더링합니다.
    utils.$('#product-results').innerHTML = '';
    utils.$('#shop-links').innerHTML = '';

    utils.$('#preview-btn').addEventListener('click', loadProducts);
    utils.$('#share-result-btn').addEventListener('click', shareResult);
    utils.$('#reset-btn').addEventListener('click', resetAll);
  }

  document.addEventListener('DOMContentLoaded', function () {
    if (document.body.dataset.page === 'result') {
      initResultPage();
    }
  });
})(window);