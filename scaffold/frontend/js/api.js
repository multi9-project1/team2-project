(function (window) {
  const utils = window.MapsiUtils;

  // 1. 기본 요청 함수
  async function request(path, options) {
    const baseUrl = utils.getApiBaseUrl().replace(/\/$/, '');
    const fullUrl = path.startsWith('http') ? path : baseUrl + path;
    
    const response = await fetch(fullUrl, {
      headers: Object.assign({ 'Content-Type': 'application/json' }, (options && options.headers) || {}),
      method: (options && options.method) || 'GET',
      body: options && options.body
    });

    const contentType = response.headers.get('content-type') || '';
    const isJson = contentType.includes('application/json');
    const body = isJson ? await response.json().catch(() => null) : await response.text().catch(() => '');

    if (!response.ok) {
      throw new Error(body.detail || body.message || 'API 요청 실패');
    }
    return body;
  }

  // 2. 설문 데이터 변환 함수
  function buildSurveyObject(state) {
    const a = state.surveyAnswers || {};
    return {
      gender: state.gender === 'M' ? 'M' : 'W',
      personal_color: state.personalColor || 'unknown',
      Qstyle_1: String(a[0] || 'A'),
      Qstyle_2: String(a[1] || 'A'),
      Qstyle_3: String(a[2] || 'A'),
      Qstyle_4: String(a[3] || 'A'),
      Qstyle_5: String(a[4] || 'A'),
      Qstyle_6: String(a[5] || 'A'),
      Qstyle_7: String(a[6] || 'A'),
      Qstyle_8: String(a[7] || 'A'),
      Qstyle_9: String(a[8] || 'A')
    };
  }

  // 3. 통신 함수 (누락되었던 함수들 복구)
  async function fetchProfileFromState(state) {
    return request('/profile', {
      method: 'POST',
      body: JSON.stringify({ survey: buildSurveyObject(state) })
    });
  }

  async function fetchRecommendationsFromState(state, profileResponse, options) {
    const payload = {
      survey: buildSurveyObject(state),
      top_n: (options && options.topN) || 5
    };
    return request('/recommendations', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  function extractProfileData(response) {
    return (response && response.user_profile) || response;
  }

  function extractResultType(data) {
    return (data && (data.primary_style || data.resultType)) || null;
  }

  // 4. 상품 데이터 규격화
  function normalizeProductItem(item, fallbackMall) {
    const source = item || {};
    return {
      brand: source.brand || source.mall_name || source.shop_name || fallbackMall || '추천 상품',
      name: source.name || source.title || source.product_name || '이름 없는 상품',
      price: source.price || source.sale_price || '가격 정보 없음',
      imageUrl: source.imageUrl || source.image_url || source.img_url || source.image || '',
      productUrl: source.productUrl || source.product_url || source.url || source.link || '',
      mall: source.mall || source.platform || fallbackMall || ''
    };
  }

  function normalizeRecommendationResponse(response) {
    const data = response || {};
    const musinsaItems = (data.musinsa || data.items || []).map(item => normalizeProductItem(item, '무신사'));
    const zigzagItems = (data.zigzag || []).map(item => normalizeProductItem(item, '지그재그'));
    return {
      musinsa: musinsaItems,
      zigzag: zigzagItems,
      all: musinsaItems.concat(zigzagItems),
      url: data.url || '',
      resultType: extractResultType(data)
    };
  }

  function buildSearchLinks(filters) {
    const q = encodeURIComponent(`${filters.category}`);
    return {
      musinsa: `https://www.musinsa.com/search/goods?keyword=${q}&gf=${filters.gender === 'W' ? 'F' : 'M'}`,
      zigzag: `https://zigzag.kr/search?keyword=${q}`
    };
  }

  function getMockProducts() {
    return { musinsa: [], zigzag: [], all: [] };
  }

  window.MapsiApi = {
    request,
    buildSurveyObject,
    fetchProfileFromState,
    fetchRecommendationsFromState,
    extractProfileData,
    extractResultType,
    normalizeRecommendationResponse,
    normalizeProductItem,
    buildSearchLinks,
    getMockProducts
  };

})(window);