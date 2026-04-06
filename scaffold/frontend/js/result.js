let resultState = requireState(['gender', 'personalColor', 'result'], './index.html');

function renderPersona() {
  const personaName = resultState.result;
  const persona = PERSONAS[personaName];
  const isFemale = resultState.gender === 'W';
  const guide = COLOR_GUIDE[resultState.personalColor] || { ms: ['블랙', '화이트', '그레이'], zz: ['블랙', '화이트', '그레이'] };
  const allColors = [...new Set([...guide.ms, ...guide.zz])].slice(0, 6);

  qs('#result-badge').textContent = `나의 맵시TI: ${persona.icon} ${personaName}`;
  qs('#result-char').style.background = persona.bg;
  qs('#result-desc-card').style.background = persona.bg;
  qs('#style-tip-card').style.background = persona.bg;
  qs('#point-color-card').style.background = persona.bg;
  qs('#char-img').textContent = isFemale ? persona.eF : persona.eM;
  qs('#result-title').textContent = `${persona.icon} ${personaName}`;
  qs('#result-sub').textContent = isFemale ? persona.tF : persona.tM;

  qs('#result-desc').innerHTML = `
    <div style="font-size:16px;color:#C94F80;margin-bottom:10px;">${persona.q}</div>
    <div class="helper-text" style="font-size:15px;line-height:1.8;color:#1E1B3A;">${persona.d}</div>
    <div class="dashed-note">✨ ${persona.pt}</div>
  `;

  qs('#result-items').innerHTML = `
    <div style="margin-top:14px;font-size:17px;color:#1E1B3A;margin-bottom:6px;">당신의 최애 아이템 🛍️</div>
    ${persona.items.map((item) => `<div class="item-row">• ${item}</div>`).join('')}
  `;

  qs('#style-tip-text').textContent = persona.tip;
  qs('#point-color-tags').innerHTML = `
    <div class="meta-text" style="margin-bottom:6px;">${resultState.personalColor} 추천 컬러</div>
    ${allColors.map((color) => `<span class="tag">${color}</span>`).join('')}
  `;
}

function buildCategoryTabs() {
  const categories = getAllowedCategories(resultState.gender);
  if (!categories.includes(resultState.selectedCat)) {
    resultState = patchAppState({ selectedCat: categories[0] });
  }

  qs('#cat-tabs').innerHTML = categories.map((category) => `
    <button class="tab-btn ${category === resultState.selectedCat ? 'is-selected' : ''}" data-cat="${category}">${category}</button>
  `).join('');

  qsa('[data-cat]').forEach((button) => {
    button.addEventListener('click', () => {
      resultState = patchAppState({ selectedCat: button.dataset.cat });
      buildCategoryTabs();
      updateSelects();
      qs('#product-results').innerHTML = '';
      qs('#shop-links').innerHTML = '';
    });
  });
}

function updateSelects() {
  const categoryFits = CAT_FITS[resultState.selectedCat] || ['레귤러핏', '루즈핏', '슬림핏'];
  const styleFits = STYLE_FIT_MAP[resultState.result] || [];
  const smartFits = categoryFits.filter((fit) => styleFits.some((baseFit) => fit.includes(baseFit)));
  const fitOptions = smartFits.length > 0
    ? [...smartFits, ...categoryFits.filter((fit) => !smartFits.includes(fit))]
    : categoryFits;

  const guide = COLOR_GUIDE[resultState.personalColor] || { ms: ['블랙', '화이트', '그레이'] };

  qs('#fit-select').innerHTML = fitOptions.map((fit) => `<option value="${fit}">${fit}</option>`).join('');
  qs('#color-select').innerHTML = guide.ms.map((color) => `<option value="${color}">${color}</option>`).join('');
}

function renderProductSection(title, items) {
  return `
    <div style="font-size:16px;color:#1E1B3A;margin:${title.includes('지그재그') ? '16px 0 12px' : '0 0 12px'};font-weight:700;">${title}</div>
    ${items.map((item) => `
      <div class="product-card" style="background:${item.bg};">
        <div class="product-thumb">${item.emoji}</div>
        <div style="flex:1;">
          <div class="product-brand">${item.brand}</div>
          <div class="product-name">${item.name}</div>
          <div class="product-price">₩${item.price}</div>
        </div>
      </div>
    `).join('')}
  `;
}

async function loadProducts() {
  const fit = qs('#fit-select').value;
  const color = qs('#color-select').value;
  const category = resultState.selectedCat;
  const button = qs('#preview-btn');

  button.disabled = true;
  button.textContent = '⏳ 크롤링 중...';

  const response = await fetchProducts({
    gender: resultState.gender,
    personalColor: resultState.personalColor,
    persona: resultState.result,
    category,
    fit,
    color
  });

  let html = renderProductSection('🛍️ 무신사 추천 상품', response.musinsa || []);
  if (resultState.gender === 'W' && response.zigzag?.length) {
    html += renderProductSection('🛍️ 지그재그 추천 상품', response.zigzag);
  }

  qs('#product-results').innerHTML = html;

  qs('#shop-links').innerHTML = `
    <a class="btn btn-dark" href="${response.links.musinsa}" target="_blank" rel="noopener noreferrer">무신사 전체 보기 →</a>
    ${resultState.gender === 'W' ? `<a class="btn btn-accent" href="${response.links.zigzag}" target="_blank" rel="noopener noreferrer">지그재그 전체 보기 →</a>` : ''}
  `;

  button.disabled = false;
  button.textContent = '⚡ 맞춤 상품 보기';
}

function shareResult() {
  const shareText = `내 맵시TI 결과는 ${resultState.result} / ${resultState.personalColor}!`;

  if (navigator.share) {
    navigator.share({
      title: '맵시TI 결과',
      text: shareText,
      url: window.location.href
    }).catch(() => {});
    return;
  }

  navigator.clipboard.writeText(shareText).then(() => {
    alert('결과 문구를 클립보드에 복사했어요!');
  }).catch(() => {
    alert('공유 기능은 실제 서비스에서 연동하면 더 자연스럽게 동작해요.');
  });
}

function resetAll() {
  resetAppState();
  navigateTo('./index.html');
}

function startLoadingAndRender() {
  buildSpinner('spinner');
  const messages = [
    '퍼스널컬러 데이터 연산 중...',
    '스타일 DNA 분석 중...',
    '맞춤 페르소나 매칭 중...',
    '무신사 상품 크롤링 준비 중...',
    '지그재그 상품 크롤링 준비 중...',
    '결과 카드 생성 중...'
  ];

  let index = 0;
  const messageNode = qs('#loading-msg');
  const interval = window.setInterval(() => {
    messageNode.textContent = messages[index % messages.length];
    index += 1;

    if (index >= messages.length + 1) {
      window.clearInterval(interval);
      qs('#loading-section').style.display = 'none';
      qs('#result-section').style.display = 'block';
      renderPersona();
      buildCategoryTabs();
      updateSelects();
    }
  }, 650);
}

document.addEventListener('DOMContentLoaded', () => {
  if (!resultState) return;

  qs('#preview-btn').addEventListener('click', loadProducts);
  qs('#share-btn').addEventListener('click', shareResult);
  qs('#reset-btn').addEventListener('click', resetAll);
  startLoadingAndRender();
});