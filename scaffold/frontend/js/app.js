import {
  CATEGORY_OPTIONS,
  COLOR_ENTRY_OPTIONS,
  COLOR_FILTER_OPTIONS,
  COOL_OPTIONS,
  FIT_QUESTION,
  MUSINSA_CATEGORY_MAP,
  PERSONAL_COLOR_OPTIONS,
  PERSONAS,
  STYLE_QUESTIONS,
  SURVEY_TOTAL_STEPS,
  TONE_QUESTIONS,
  WARM_OPTIONS,
  personalColorLabel,
  resolveGenderImagePath,
  resolvePersonaImagePath,
} from './constants.js';
import {
  analyzeProfile,
  crawlMusinsa,
  crawlZigzag,
  getRecommendations,
} from './api.js';

const screenHost = document.getElementById('screenHost');
const toast = document.getElementById('toast');
const modalRoot = document.getElementById('modalRoot');
const modalBody = document.getElementById('modalBody');
const modalConfirmBtn = document.getElementById('modalConfirmBtn');

const initialSurvey = () => ({
  gender: '',
  personal_color: '',
  Q1: '',
  Q2: '',
  Q3: '',
  Qwarm: '',
  Qcool: '',
  Qstyle_1: '',
  Qstyle_2: '',
  Qstyle_3: '',
  Qstyle_4: '',
  Qstyle_5: '',
  Qstyle_6: '',
  Qstyle_7: '',
  Qstyle_8: '',
  Qstyle_9: '',
});

const state = {
  screen: 'splash',
  survey: initialSurvey(),
  colorFlowMode: '',
  toneIndex: 0,
  toneBranch: '',
  styleIndex: 0,
  selectedCategory: '상의',
  selectedColorFilter: '',
  isLoading: false,
  pendingColorSelection: null,
  result: null,
  musinsa: null,
  zigzag: null,
};

function showToast(message) {
  toast.textContent = message;
  toast.classList.add('show');
  window.clearTimeout(showToast._timer);
  showToast._timer = window.setTimeout(() => toast.classList.remove('show'), 2200);
}

function openModal(html, onConfirm) {
  modalBody.innerHTML = html;
  modalRoot.classList.remove('hidden');
  modalRoot.setAttribute('aria-hidden', 'false');
  modalConfirmBtn.onclick = () => {
    modalRoot.classList.add('hidden');
    modalRoot.setAttribute('aria-hidden', 'true');
    if (typeof onConfirm === 'function') onConfirm();
  };
}

function imageOrFallback(src, alt, fallbackLabel, className = '') {
  return `
    <img src="${src}" alt="${escapeHtml(alt)}" class="${className}" onerror="this.outerHTML='<div class=\'image-fallback\'><div><strong>${escapeAttr(
      fallbackLabel,
    )}</strong><small>이미지 파일을 assets/images 폴더에 넣어주세요.</small></div></div>'" />
  `;
}

function escapeHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function escapeAttr(value) {
  return escapeHtml(value).replace(/\n/g, ' ');
}

function setScreen(screen) {
  state.screen = screen;
  render();
}

function resetToneState() {
  state.survey.Q1 = '';
  state.survey.Q2 = '';
  state.survey.Q3 = '';
  state.survey.Qwarm = '';
  state.survey.Qcool = '';
  state.toneIndex = 0;
  state.toneBranch = '';
}

function resetForRestart() {
  state.screen = 'splash';
  state.survey = initialSurvey();
  state.colorFlowMode = '';
  state.toneIndex = 0;
  state.toneBranch = '';
  state.styleIndex = 0;
  state.selectedCategory = '상의';
  state.selectedColorFilter = '';
  state.isLoading = false;
  state.pendingColorSelection = null;
  state.result = null;
  state.musinsa = null;
  state.zigzag = null;
  render();
}

function buildRecommendationPayload() {
  return {
    survey: { ...state.survey },
    top_n: 5,
    allow_mock_data: true,
    prefer_extracted_dataset: true,
  };
}

function buildCrawlPayload(platform) {
  const categoryName = platform === 'musinsa'
    ? (MUSINSA_CATEGORY_MAP[state.selectedCategory] || '상의')
    : state.selectedCategory;

  return {
    survey: { ...state.survey },
    category_name: categoryName,
    selected_color: state.selectedColorFilter || undefined,
    allow_mock_data: true,
    top_n: 3,
  };
}

function inferToneBranch() {
  const answers = [state.survey.Q1, state.survey.Q2, state.survey.Q3];
  const warmVotes = answers.filter((v) => v === 'A').length;
  const coolVotes = answers.filter((v) => v === 'B').length;
  return warmVotes > coolVotes ? 'warm' : 'cool';
}

function resolvedPersona() {
  const userProfile = state.result?.recommendation?.user_profile || {};
  const primaryStyle = userProfile.primary_style || '';
  return PERSONAS[primaryStyle] || PERSONAS.casual;
}

function resolvedResultImage() {
  const persona = resolvedPersona();
  return resolvePersonaImagePath(persona.code, state.survey.gender || 'W');
}

function resultColorChips() {
  const userProfile = state.result?.recommendation?.user_profile || {};
  const colors = userProfile.representative_colors || [];
  return colors.length ? colors : [personalColorLabel(state.survey.personal_color)];
}

function fitLabel() {
  return state.survey.Qstyle_3 === 'B' ? '루즈 / 오버 핏' : '타이트 / 노멀 핏';
}

function stripMarkdownDecorators(value) {
  return String(value || '').replace(/\*\*/g, '').replace(/\*/g, '').trim();
}

async function runMainAnalysis() {
  state.isLoading = true;
  state.musinsa = null;
  state.zigzag = null;
  setScreen('loading');

  try {
    const surveyPayload = { survey: { ...state.survey } };
    const [profile, recommendation] = await Promise.all([
      analyzeProfile(surveyPayload),
      getRecommendations(buildRecommendationPayload()),
    ]);
    state.result = { profile, recommendation };
    state.styleIndex = 0;
    state.isLoading = false;
    setScreen('result');
  } catch (error) {
    state.isLoading = false;
    setScreen('fit');
    showToast(error instanceof Error ? error.message : '추천 요청에 실패했어요.');
  }
}

async function runShoppingCuration() {
  if (!state.result) {
    showToast('먼저 결과를 확인한 뒤 상품을 불러와 주세요.');
    return;
  }

  showToast('무신사와 지그재그 상품을 불러오는 중이에요...');

  try {
    const [musinsaResult, zigzagResult] = await Promise.allSettled([
      crawlMusinsa(buildCrawlPayload('musinsa')),
      crawlZigzag(buildCrawlPayload('zigzag')),
    ]);

    if (musinsaResult.status === 'fulfilled') state.musinsa = musinsaResult.value;
    if (zigzagResult.status === 'fulfilled') state.zigzag = zigzagResult.value;

    if (musinsaResult.status === 'rejected' && zigzagResult.status === 'rejected') {
      throw musinsaResult.reason || zigzagResult.reason || new Error('상품을 불러오지 못했어요.');
    }

    render();
    showToast('맞춤 상품을 불러왔어요!');
  } catch (error) {
    showToast(error instanceof Error ? error.message : '상품 불러오기에 실패했어요.');
  }
}

function shareResult() {
  if (!state.result) return;
  const persona = resolvedPersona();
  const summary = stripMarkdownDecorators(state.result.recommendation?.preference_analysis?.text || `${persona.label} 타입으로 분석되었어요.`);
  const shareText = `맵시TI 결과\n${persona.label}\n${summary}`;

  if (navigator.share) {
    navigator
      .share({ title: '맵시TI 결과', text: shareText })
      .catch(() => undefined);
    return;
  }

  navigator.clipboard
    .writeText(shareText)
    .then(() => showToast('결과 문구를 클립보드에 복사했어요.'))
    .catch(() => showToast('공유 문구 복사에 실패했어요.'));
}

function renderSplash() {
  return `
    <section class="screen active">
      <div class="pcard hero-card card-stack">
        <div class="hero-icon">👗</div>
        <h2 class="screen-title">성별 & 퍼스널컬러 분석 +<br />스타일 설문 응답으로<br />나만의 패션 DNA 발견!</h2>
      </div>

      <div class="pcard feature-card">
        <ul class="feature-list">
          <li><span>🧁</span><span>10가지 스타일 페르소나 분석</span></li>
          <li><span>🛍️</span><span>무신사 & 지그재그 맞춤 상품 추천</span></li>
          <li><span>🎨</span><span>퍼스널컬러 맞춤 컬러 가이드</span></li>
          <li><span>📸</span><span>결과 카드 SNS 공유 가능</span></li>
        </ul>
      </div>

      <div class="btn-row">
        <button class="btn btn-primary" type="button" data-action="go-gender">시작하기 <span class="emoji">💫</span></button>
      </div>
    </section>
  `;
}

function renderGender() {
  return `
    <section class="screen active card-stack">
      <div class="pcard">
        <h2 class="section-title">나는 어떤 스타일러?</h2>
        <p class="section-note">성별을 선택해줘! 결과 캐릭터가 달라져 👀</p>
        <div class="gender-grid">
          ${['W', 'M']
            .map((gender) => {
              const label = gender === 'W' ? '여성' : '남성';
              const active = state.survey.gender === gender ? ' is-active' : '';
              return `
                <button type="button" class="gender-card${active}" data-gender="${gender}">
                  ${imageOrFallback(resolveGenderImagePath(gender), label, `${gender === 'W' ? 'female_select.png' : 'male_select.png'}`)}
                  <div class="gender-label">${label}</div>
                  <div class="gender-note">${gender === 'W' ? '무신사 + 지그재그' : '무신사'}</div>
                </button>
              `;
            })
            .join('')}
        </div>
      </div>

      <div class="btn-row">
        <button class="btn btn-secondary" type="button" data-action="back-splash">← 뒤로</button>
        <button class="btn btn-accent" type="button" data-action="go-color-intro">다음으로 →</button>
      </div>
    </section>
  `;
}

function renderColorIntro() {
  return `
    <section class="screen active card-stack">
      <div class="pcard">
        <h2 class="section-title">퍼스널컬러 알아? 🎨</h2>
        <p class="section-note">알고 있으면 바로 선택, 모르면 간이 진단으로 찾아줄게!</p>
        <div class="card-stack">
          ${COLOR_ENTRY_OPTIONS.map((option) => {
            const active = state.colorFlowMode === option.value ? ' is-active' : '';
            return `
              <button type="button" class="option-card know-card${active}" data-color-flow="${option.value}">
                <span class="option-title">${option.title} <span class="emoji">${option.emoji}</span></span>
                <span class="choice-description">${option.description}</span>
              </button>
            `;
          }).join('')}
        </div>
      </div>

      <div class="btn-row">
        <button class="btn btn-secondary" type="button" data-action="back-gender">← 뒤로</button>
        <button class="btn btn-accent" type="button" data-action="confirm-color-flow">다음으로 →</button>
      </div>
    </section>
  `;
}

function renderDirectColorSelect() {
  return `
    <section class="screen active card-stack">
      <div class="pcard">
        <h2 class="section-title">나에게 어울리는 색깔은? 🎨</h2>
        <p class="section-note">12가지 퍼스널 컬러 중에서 가장 잘 맞는 느낌을 골라봐!</p>
        <div class="option-grid cols-2">
          ${PERSONAL_COLOR_OPTIONS.map((item) => {
            const active = state.survey.personal_color === item.value ? ' is-active' : '';
            return `
              <button type="button" class="option-card color-card${active}" data-color-value="${item.value}">
                <span class="option-badge">${item.emoji}</span>
                <strong class="option-title">${item.label}</strong>
                <span class="choice-description">${item.mood}</span>
              </button>
            `;
          }).join('')}
        </div>
      </div>

      <div class="btn-row">
        <button class="btn btn-secondary" type="button" data-action="back-color-intro">← 이전 단계로</button>
      </div>
    </section>
  `;
}

function renderToneQuestion() {
  const question = TONE_QUESTIONS[state.toneIndex];
  const total = TONE_QUESTIONS.length;
  const progress = Math.round(((state.toneIndex + 1) / total) * 100);
  return `
    <section class="screen active card-stack">
      <div class="pcard progress-card">
        <div class="progress-meta">
          <span class="progress-caption">질문 ${state.toneIndex + 1} / ${total}</span>
          <span class="progress-caption">${progress}%</span>
        </div>
        <div class="pbar-bg"><div class="pbar-fill" style="width:${progress}%"></div></div>
      </div>

      <div class="pcard card-stack">
        <div>
          <p class="small-note">${question.stepLabel}</p>
          <h2 class="section-title">${question.title} 🌈</h2>
          <p class="section-note">${question.subtitle}</p>
        </div>
        <h3>${question.question}</h3>
        <div class="option-grid cols-2">
          ${question.answers
            .map((answer) => `
              <button type="button" class="choice-card" data-tone-key="${question.key}" data-tone-value="${answer.value}">
                <span class="choice-letter">${answer.value}</span>
                <div class="choice-text">
                  <strong>${answer.title}</strong>
                  <span class="choice-description">${answer.description}</span>
                </div>
              </button>
            `)
            .join('')}
        </div>
      </div>

      <div class="btn-row">
        <button class="btn btn-secondary" type="button" data-action="back-tone">← 뒤로</button>
      </div>
    </section>
  `;
}

function renderToneBranchSelect() {
  const options = state.toneBranch === 'warm' ? WARM_OPTIONS : COOL_OPTIONS;
  const branchLabel = state.toneBranch === 'warm' ? '웜 🌼' : '쿨 ❄️';
  return `
    <section class="screen active card-stack">
      <div class="pcard">
        <h2 class="section-title">나에게 어울리는 색깔은? 🎨</h2>
        <p class="section-note">단계 결과: <strong>${branchLabel}</strong><br />내 피부에 가장 잘 어울리는 느낌을 골라봐!</p>
        <div class="card-stack">
          ${options
            .map(
              (item) => `
                <button type="button" class="option-card color-list-item" data-diagnosed-color="${item.value}" data-followup="${item.followup}">
                  <span class="option-badge">${item.emoji}</span>
                  <strong class="option-title">${item.label}</strong>
                  <small>${item.description}</small>
                </button>
              `,
            )
            .join('')}
        </div>
      </div>

      <div class="btn-row">
        <button class="btn btn-secondary" type="button" data-action="back-tone-branch">← 이전 단계로</button>
      </div>
    </section>
  `;
}

function renderStyleQuestion() {
  const question = STYLE_QUESTIONS[state.styleIndex];
  const current = state.styleIndex + 1;
  const progress = Math.round((current / SURVEY_TOTAL_STEPS) * 100);
  return `
    <section class="screen active card-stack">
      <div class="pcard progress-card">
        <div class="progress-meta">
          <span class="progress-caption">Q${current} / ${SURVEY_TOTAL_STEPS}</span>
          <span class="progress-caption">${progress}%</span>
        </div>
        <div class="pbar-bg"><div class="pbar-fill" style="width:${progress}%"></div></div>
      </div>

      <div class="pcard card-stack">
        <p class="small-note">스타일 설문</p>
        <h2 class="section-title">${question.title}</h2>
        <div class="card-stack">
          ${question.answers
            .map((answer) => {
              const active = state.survey[question.key] === answer.value ? ' is-active' : '';
              return `
                <button type="button" class="choice-card${active}" data-style-key="${question.key}" data-style-value="${answer.value}">
                  <span class="choice-letter">${answer.value}</span>
                  <div class="choice-text">
                    <strong>${answer.title}</strong>
                    <span class="choice-description">${answer.description}</span>
                  </div>
                </button>
              `;
            })
            .join('')}
        </div>
      </div>

      <div class="btn-row">
        <button class="btn btn-secondary" type="button" data-action="back-style">← 이전</button>
        <button class="btn btn-accent" type="button" data-action="next-style">다음 →</button>
      </div>
    </section>
  `;
}

function renderFitQuestion() {
  const progress = 100;
  return `
    <section class="screen active card-stack">
      <div class="pcard progress-card">
        <div class="progress-meta">
          <span class="progress-caption">Q${SURVEY_TOTAL_STEPS} / ${SURVEY_TOTAL_STEPS}</span>
          <span class="progress-caption">${progress}%</span>
        </div>
        <div class="pbar-bg"><div class="pbar-fill" style="width:${progress}%"></div></div>
      </div>

      <div class="pcard card-stack">
        <p class="small-note">마지막 단계 · 핏</p>
        <h2 class="section-title">${FIT_QUESTION.title}</h2>
        <div class="card-stack">
          ${FIT_QUESTION.answers
            .map((answer) => {
              const active = state.survey[FIT_QUESTION.key] === answer.value ? ' is-active' : '';
              return `
                <button type="button" class="choice-card${active}" data-fit-value="${answer.value}">
                  <span class="choice-letter">${answer.value}</span>
                  <div class="choice-text">
                    <strong>${answer.title}</strong>
                    <span class="choice-description">${answer.description}</span>
                  </div>
                </button>
              `;
            })
            .join('')}
        </div>
      </div>

      <div class="btn-row">
        <button class="btn btn-secondary" type="button" data-action="back-fit">← 이전</button>
        <button class="btn btn-accent" type="button" data-action="show-result">결과 보기 ✨</button>
      </div>
    </section>
  `;
}

function renderLoading() {
  return `
    <section class="screen active card-stack">
      <div class="pcard loading-card">
        <h2 class="section-title">맵시 분석 중... ✨</h2>
        <div class="spinner">${Array.from({ length: 16 }, () => '<span></span>').join('')}</div>
        <p class="section-note">추천 상품 요청 중...<br />잠깐만 기다려줘!</p>
      </div>
    </section>
  `;
}

function renderProductSection(title, result) {
  const items = result?.items || [];
  const platform = result?.platform || '';
  return `
    <section class="product-section card-stack">
      <h3>${title}</h3>
      ${items.length
        ? `<div class="product-list">
            ${items
              .map((item) => `
                <article class="product-card">
                  <div class="product-thumb">
                    ${item.img_url
                      ? imageOrFallback(item.img_url, item.title || title, item.title || '상품 이미지')
                      : '<div class="image-fallback"><div><strong>상품 이미지</strong><small>img_url 응답 대기 중</small></div></div>'}
                  </div>
                  <div>
                    <div class="product-brand">${escapeHtml(item.brand || item.mall_name || platform || '-')}</div>
                    <div class="product-title">${escapeHtml(item.title || '상품명 없음')}</div>
                    <div class="product-price">${escapeHtml(item.price || '-')}</div>
                    <div class="product-meta">${escapeHtml(result.search_keyword || '')}${result.selected_color ? ` · ${escapeHtml(result.selected_color)}` : ''}</div>
                  </div>
                </article>
              `)
              .join('')}
          </div>`
        : `<div class="empty-box">아직 불러온 상품이 없어요.<br />아래 쇼핑 큐레이션에서 맞춤 상품 보기를 눌러주세요.</div>`}
    </section>
  `;
}

function renderResult() {
  const recommendation = state.result?.recommendation || {};
  const userProfile = recommendation.user_profile || {};
  const persona = resolvedPersona();
  const summaryRaw = recommendation.preference_analysis?.text || `당신의 스타일은 ${persona.label}에 가까워 보여!`;
  const summary = stripMarkdownDecorators(summaryRaw);
  const colors = resultColorChips();
  const fit = fitLabel();

  return `
    <section class="screen active result-screen card-stack">
      <div class="pcard loading-card">
        <div class="persona-banner">나의 맵시TI = ${persona.label}</div>
        <div class="pcard persona-result-main">
          <div class="persona-portrait">
            ${imageOrFallback(resolvedResultImage(), persona.label, `${persona.code}_${String(state.survey.gender || 'W').toLowerCase() === 'm' ? 'm' : 'w'}.png`)}
          </div>
          <h2 class="persona-card-title">${persona.label}</h2>
          <p class="result-caption">${persona.headline}</p>
        </div>
      </div>

      <div class="pcard card-stack">
        <p>${escapeHtml(persona.tagline)}</p>
        <p class="section-note">${escapeHtml(persona.description)}</p>
        <div class="quote-box">${escapeHtml(persona.point)}</div>
        <div>
          <h3>당신의 최애 아이템 🛍️</h3>
          <ul class="bullets">
            ${persona.items.map((item) => `<li>${escapeHtml(item)}</li>`).join('')}
          </ul>
        </div>
        <div class="tips-grid">
          <div class="tip-card">
            <h4>🪄 스타일 팁</h4>
            <p>${escapeHtml(persona.styleTip)}</p>
          </div>
          <div class="tip-card">
            <h4>🎨 포인트 컬러</h4>
            <div class="color-text-list">
              ${colors.map((color) => `<span class="color-text-chip">${escapeHtml(color)}</span>`).join('')}
            </div>
          </div>
        </div>
      </div>

      <div class="pcard muted-box card-stack">
        <h3>분석 요약</h3>
        <p class="section-note">${escapeHtml(summary)}</p>
        <div class="inline-actions">
          <span class="chip-soft">성별: ${escapeHtml(state.survey.gender === 'M' ? '남성' : '여성')}</span>
          <span class="chip-soft">퍼스널컬러: ${escapeHtml(personalColorLabel(state.survey.personal_color))}</span>
          <span class="chip-soft">핏: ${escapeHtml(fit)}</span>
        </div>
      </div>
      <div class="pcard filter-card card-stack">
        <div class="filter-card-head">
          <div>
            <h3>🛍️ 쇼핑 큐레이션</h3>
            <p class="filter-help">카테고리와 컬러를 정하면 무신사 + 지그재그 상품을 함께 불러와요.</p>
          </div>
        </div>
        <div class="style-pills">
          ${CATEGORY_OPTIONS.map((category) => {
            const active = state.selectedCategory === category ? ' is-active' : '';
            return `<button type="button" class="filter-pill${active}" data-category-pill="${category}">${category}</button>`;
          }).join('')}
        </div>
        <div class="field-grid">
          <div class="field-row">
            <label for="fitField">핏 선택</label>
            <input id="fitField" class="input" value="${escapeAttr(fit)}" readonly />
          </div>
          <div class="field-row">
            <label for="colorField">컬러 선택</label>
            <select id="colorField" class="select">
              ${COLOR_FILTER_OPTIONS.map((option) => `<option value="${option.value}"${state.selectedColorFilter === option.value ? ' selected' : ''}>${option.label}</option>`).join('')}
            </select>
          </div>
        </div>
        <button class="btn btn-mint" type="button" data-action="load-products">⚡ 맞춤 상품 보기</button>
      </div>

      ${renderProductSection('🛍️ 무신사 추천 상품', state.musinsa)}
      ${renderProductSection('🛍️ 지그재그 추천 상품', state.zigzag)}

      <div class="result-actions">
        <button class="btn btn-primary" type="button" data-action="share-result">📸 결과 공유</button>
        <button class="btn btn-dark" type="button" data-action="restart">🔄 다시하기</button>
      </div>
    </section>
  `;
}

function render() {
  let html = '';
  switch (state.screen) {
    case 'splash':
      html = renderSplash();
      break;
    case 'gender':
      html = renderGender();
      break;
    case 'colorIntro':
      html = renderColorIntro();
      break;
    case 'directColor':
      html = renderDirectColorSelect();
      break;
    case 'toneQuestion':
      html = renderToneQuestion();
      break;
    case 'toneBranch':
      html = renderToneBranchSelect();
      break;
    case 'style':
      html = renderStyleQuestion();
      break;
    case 'fit':
      html = renderFitQuestion();
      break;
    case 'loading':
      html = renderLoading();
      break;
    case 'result':
      html = renderResult();
      break;
    default:
      html = renderSplash();
      break;
  }
  screenHost.innerHTML = html;
  bindEvents();
}

function bindEvents() {
  screenHost.querySelector('[data-action="go-gender"]')?.addEventListener('click', () => setScreen('gender'));
  screenHost.querySelector('[data-action="back-splash"]')?.addEventListener('click', () => setScreen('splash'));
  screenHost.querySelector('[data-action="back-gender"]')?.addEventListener('click', () => setScreen('gender'));
  screenHost.querySelector('[data-action="back-color-intro"]')?.addEventListener('click', () => setScreen('colorIntro'));
  screenHost.querySelector('[data-action="back-tone-branch"]')?.addEventListener('click', () => {
    state.toneIndex = TONE_QUESTIONS.length - 1;
    setScreen('toneQuestion');
  });

  screenHost.querySelectorAll('[data-gender]').forEach((element) => {
    element.addEventListener('click', () => {
      state.survey.gender = element.dataset.gender;
      render();
    });
  });

  screenHost.querySelector('[data-action="go-color-intro"]')?.addEventListener('click', () => {
    if (!state.survey.gender) {
      showToast('먼저 성별을 선택해줘!');
      return;
    }
    setScreen('colorIntro');
  });

  screenHost.querySelectorAll('[data-color-flow]').forEach((element) => {
    element.addEventListener('click', () => {
      state.colorFlowMode = element.dataset.colorFlow;
      render();
    });
  });

  screenHost.querySelector('[data-action="confirm-color-flow"]')?.addEventListener('click', () => {
    if (!state.colorFlowMode) {
      showToast('퍼스널컬러 선택 방식을 골라줘!');
      return;
    }
    if (state.colorFlowMode === 'direct') {
      setScreen('directColor');
      return;
    }
    state.survey.personal_color = 'unknown';
    resetToneState();
    setScreen('toneQuestion');
  });

  screenHost.querySelectorAll('[data-color-value]').forEach((element) => {
    element.addEventListener('click', () => {
      const value = element.dataset.colorValue;
      const label = personalColorLabel(value);
      state.pendingColorSelection = { value, followup: '' };
      openModal(`진단 완료! 당신에게 잘 어울리는 컬러는 <strong>${escapeHtml(label)}</strong> 타입이에요 🫶`, () => {
        state.survey.personal_color = value;
        setScreen('style');
      });
    });
  });

  screenHost.querySelectorAll('[data-tone-key]').forEach((element) => {
    element.addEventListener('click', () => {
      const key = element.dataset.toneKey;
      const value = element.dataset.toneValue;
      state.survey[key] = value;
      if (state.toneIndex < TONE_QUESTIONS.length - 1) {
        state.toneIndex += 1;
        render();
      } else {
        state.toneBranch = inferToneBranch();
        setScreen('toneBranch');
      }
    });
  });

  screenHost.querySelector('[data-action="back-tone"]')?.addEventListener('click', () => {
    if (state.toneIndex === 0) {
      setScreen('colorIntro');
      return;
    }
    state.toneIndex -= 1;
    render();
  });

  screenHost.querySelectorAll('[data-diagnosed-color]').forEach((element) => {
    element.addEventListener('click', () => {
      const value = element.dataset.diagnosedColor;
      const followup = element.dataset.followup;
      const label = personalColorLabel(value);
      openModal(`진단 완료! 당신은 <strong>${escapeHtml(label)}</strong> 타입이에요 🧠`, () => {
        state.survey.personal_color = value;
        if (state.toneBranch === 'warm') state.survey.Qwarm = followup;
        if (state.toneBranch === 'cool') state.survey.Qcool = followup;
        setScreen('style');
      });
    });
  });

  screenHost.querySelectorAll('[data-style-key]').forEach((element) => {
    element.addEventListener('click', () => {
      const key = element.dataset.styleKey;
      const value = element.dataset.styleValue;
      state.survey[key] = value;
      render();
    });
  });

  screenHost.querySelector('[data-action="back-style"]')?.addEventListener('click', () => {
    if (state.styleIndex === 0) {
      if (state.colorFlowMode === 'direct') {
        setScreen('directColor');
      } else {
        setScreen('toneBranch');
      }
      return;
    }
    state.styleIndex -= 1;
    render();
  });

  screenHost.querySelector('[data-action="next-style"]')?.addEventListener('click', () => {
    const currentQuestion = STYLE_QUESTIONS[state.styleIndex];
    if (!state.survey[currentQuestion.key]) {
      showToast('답변을 선택해줘!');
      return;
    }
    if (state.styleIndex < STYLE_QUESTIONS.length - 1) {
      state.styleIndex += 1;
      render();
      return;
    }
    setScreen('fit');
  });

  screenHost.querySelectorAll('[data-fit-value]').forEach((element) => {
    element.addEventListener('click', () => {
      state.survey.Qstyle_3 = element.dataset.fitValue;
      render();
    });
  });

  screenHost.querySelector('[data-action="back-fit"]')?.addEventListener('click', () => {
    setScreen('style');
  });

  screenHost.querySelector('[data-action="show-result"]')?.addEventListener('click', () => {
    if (!state.survey.Qstyle_3) {
      showToast('핏 답변을 선택해줘!');
      return;
    }
    runMainAnalysis();
  });

  screenHost.querySelectorAll('[data-category-pill]').forEach((element) => {
    element.addEventListener('click', () => {
      state.selectedCategory = element.dataset.categoryPill;
      render();
    });
  });

  screenHost.querySelector('#colorField')?.addEventListener('change', (event) => {
    state.selectedColorFilter = event.target.value;
  });

  screenHost.querySelector('[data-action="load-products"]')?.addEventListener('click', () => {
    runShoppingCuration();
  });

  screenHost.querySelector('[data-action="share-result"]')?.addEventListener('click', shareResult);
  screenHost.querySelector('[data-action="restart"]')?.addEventListener('click', resetForRestart);
}

function boot() {
  render();
}

boot();
