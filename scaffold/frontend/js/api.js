(function (window) {
  const utils = window.MapsiUtils;

  async function request(path, options) {
    const response = await fetch(utils.getApiBaseUrl() + path, {
      headers: Object.assign({ 'Content-Type': 'application/json' }, (options && options.headers) || {}),
      credentials: 'same-origin',
      method: 'GET',
      ...(options || {})
    });

    const contentType = response.headers.get('content-type') || '';
    const isJson = contentType.includes('application/json');
    const body = isJson ? await response.json().catch(function () { return null; }) : await response.text().catch(function () { return ''; });

    if (!response.ok) {
      const message = typeof body === 'object' && body
        ? (body.detail || body.message || JSON.stringify(body))
        : (body || (response.status + ' ' + response.statusText));
      const error = new Error(message || 'API 요청에 실패했습니다.');
      error.status = response.status;
      error.body = body;
      throw error;
    }

    return body;
  }

  async function tryRequestVariants(path, payloads) {
    let lastError = null;
    for (let index = 0; index < payloads.length; index += 1) {
      try {
        return await request(path, {
          method: 'POST',
          body: JSON.stringify(payloads[index])
        });
      } catch (error) {
        lastError = error;
        if (![400, 422].includes(error.status)) {
          throw error;
        }
      }
    }
    throw lastError || new Error(path + ' 요청에 실패했습니다.');
  }

  function buildSurveyMetadata(state) {
    return {
      source: 'frontend-web',
      question_count: Object.keys(state.surveyAnswers || {}).length,
      completed_at: new Date().toISOString()
    };
  }

  function buildProfilePayload(state) {
    return {
      gender: state.gender,
      personal_color: state.personalColor,
      survey_answers: state.surveyAnswers || {},
      metadata: buildSurveyMetadata(state)
    };
  }

  function buildSurveyObject(state) {
    const a = state.surveyAnswers || {};
    return {
      gender: state.gender,
      personal_color: state.personalColor,
      Qstyle_1: a[0] || null,
      Qstyle_2: a[1] || null,
      Qstyle_3: a[2] || null,
      Qstyle_4: a[3] || null,
      Qstyle_5: a[4] || null,
      Qstyle_6: a[5] || null,
      Qstyle_7: a[6] || null,
      Qstyle_8: a[7] || null,
      Qstyle_9: a[8] || null
    };
  }

  function buildProfilePayloadVariants(state) {
    return [{ survey: buildSurveyObject(state) }];
  }

  function buildRecommendationPayload(state, extra) {
    const payload = {
      top_n: (extra && extra.topN) || 5,
      category: extra && extra.category ? extra.category : null,
      fit: extra && extra.fit ? extra.fit : null,
      color: extra && extra.color ? extra.color : null,
      metadata: buildSurveyMetadata(state)
    };

    if (state.resultType) payload.result_type = state.resultType;
    if (state.gender) payload.gender = state.gender;
    if (state.personalColor) payload.personal_color = state.personalColor;
    if (state.surveyAnswers) payload.survey_answers = state.surveyAnswers;

    return payload;
  }

  function extractProfileData(profileResponse) {
    if (!profileResponse || typeof profileResponse !== 'object') return null;
    return profileResponse.profile || (profileResponse.data && profileResponse.data.profile) || profileResponse.parsed_profile || profileResponse.result || profileResponse;
  }

  function extractResultType(value) {
    if (!value) return null;
    if (typeof value === 'string') return value;
    if (typeof value !== 'object') return null;
    return utils.pickFirst(value, [
      'result_type',
      'persona',
      'persona_name',
      'persona_type',
      'style_type',
      'style_name',
      'type',
      'label'
    ], null);
  }

  function buildRecommendationPayloadVariants(state, _profileResponse, extra) {
    return [{
      survey: buildSurveyObject(state),
      top_n: (extra && extra.topN) || 5
    }];
  }

  async function fetchProfileFromState(state) {
    return tryRequestVariants('/profile', buildProfilePayloadVariants(state));
  }

  async function fetchRecommendationsFromState(state, profileResponse, extra) {
    return tryRequestVariants('/recommendations', buildRecommendationPayloadVariants(state, profileResponse, extra));
  }

  function normalizeProductItem(item, fallbackMall) {
    const source = item || {};
    const reasonRaw = utils.pickFirst(source, ['reason', 'recommend_reason', 'explanation', 'description'], null)
      || (Array.isArray(source.reasons) ? source.reasons[0] : null)
      || '';
    return {
      brand: utils.pickFirst(source, ['brand', 'mall_name', 'shop_name', 'store_name', 'source'], fallbackMall || '추천 상품'),
      name: utils.pickFirst(source, ['name', 'title', 'product_name', 'item_name', 'item_id'], '이름 없는 상품'),
      price: utils.pickFirst(source, ['price', 'sale_price', 'display_price', 'formatted_price'], ''),
      imageUrl: utils.pickFirst(source, ['image_url', 'image', 'imageUrl', 'thumbnail_url', 'thumbnail'], ''),
      productUrl: utils.pickFirst(source, ['product_url', 'url', 'link', 'deeplink', 'deep_link'], ''),
      mall: utils.pickFirst(source, ['mall', 'platform', 'source', 'site_name'], fallbackMall || ''),
      reason: reasonRaw,
      raw: source
    };
  }

  function normalizeRecommendationResponse(response) {
    const root = response && response.data ? response.data : (response || {});
    const musinsaRaw = root.musinsa || root.musinsa_items || root.musinsa_products || root.musinsa_recommendations || [];
    const zigzagRaw = root.zigzag || root.zigzag_items || root.zigzag_products || root.zigzag_recommendations || [];
    const genericRaw = root.recommendations || root.items || root.products || root.results || [];

    let musinsa = Array.isArray(musinsaRaw) ? musinsaRaw : [];
    let zigzag = Array.isArray(zigzagRaw) ? zigzagRaw : [];
    let all = Array.isArray(genericRaw) ? genericRaw : [];

    if (!musinsa.length && !zigzag.length && all.length) {
      musinsa = all.filter(function (item) {
        const source = String(utils.pickFirst(item, ['mall', 'platform', 'source', 'site_name'], '')).toLowerCase();
        return source.includes('musinsa') || source.includes('무신사') || !source;
      });
      zigzag = all.filter(function (item) {
        const source = String(utils.pickFirst(item, ['mall', 'platform', 'source', 'site_name'], '')).toLowerCase();
        return source.includes('zigzag') || source.includes('지그재그');
      });
    }

    const normalizedMusinsa = musinsa.map(function (item) { return normalizeProductItem(item, '무신사'); });
    const normalizedZigzag = zigzag.map(function (item) { return normalizeProductItem(item, '지그재그'); });
    const normalizedAll = (all.length ? all : normalizedMusinsa.concat(normalizedZigzag)).map(function (item) {
      return normalizeProductItem(item, utils.pickFirst(item, ['mall', 'platform', 'source'], '추천 상품'));
    });

    return {
      raw: response,
      resultType: extractResultType(root) || extractResultType(root.profile) || extractResultType(root.metadata),
      musinsa: normalizedMusinsa,
      zigzag: normalizedZigzag,
      all: normalizedAll,
      message: utils.pickFirst(root, ['message', 'detail'], ''),
      links: {
        musinsa: utils.pickFirst(root, ['musinsa_url', 'musinsa_link'], ''),
        zigzag: utils.pickFirst(root, ['zigzag_url', 'zigzag_link'], '')
      }
    };
  }

  function buildSearchLinks(filters) {
    const genderLabel = filters.gender === 'W' ? '여성' : '남성';
    const musinsaQuery = encodeURIComponent(filters.fit + ' ' + filters.color + ' ' + genderLabel + ' ' + filters.category);
    const zigzagQuery = encodeURIComponent(filters.fit + ' ' + filters.color + ' ' + filters.category);

    return {
      musinsa: 'https://www.musinsa.com/search/goods?keyword=' + musinsaQuery + '&gf=' + (filters.gender === 'W' ? 'F' : 'M'),
      zigzag: 'https://zigzag.kr/search?keyword=' + zigzagQuery
    };
  }

  function getMockProducts(filters) {
    const musinsa = [
      { brand: '무신사 스탠다드', name: filters.color + ' ' + filters.fit + ' ' + filters.category, price: '29,900', mall: '무신사' },
      { brand: '커버낫', name: '베이직 ' + filters.category + ' (' + filters.fit + ')', price: '49,000', mall: '무신사' },
      { brand: '디스이즈네버댓', name: filters.color + ' 로고 ' + filters.category, price: '79,000', mall: '무신사' }
    ].map(function (item) { return normalizeProductItem(item, '무신사'); });

    const zigzag = filters.gender === 'W'
      ? [
          { brand: '지그재그PICK', name: filters.color + ' ' + filters.fit + ' 원피스', price: '35,000', mall: '지그재그' },
          { brand: '스타일난다', name: '트렌디 ' + filters.category + ' (' + filters.color + ')', price: '28,000', mall: '지그재그' },
          { brand: '에이블리', name: '데님 ' + filters.fit + ' ' + filters.category, price: '55,000', mall: '지그재그' }
        ].map(function (item) { return normalizeProductItem(item, '지그재그'); })
      : [];

    return { musinsa: musinsa, zigzag: zigzag, all: musinsa.concat(zigzag) };
  }

  window.MapsiApi = {
    request: request,
    buildProfilePayload: buildProfilePayload,
    buildRecommendationPayload: buildRecommendationPayload,
    fetchProfileFromState: fetchProfileFromState,
    fetchRecommendationsFromState: fetchRecommendationsFromState,
    extractProfileData: extractProfileData,
    extractResultType: extractResultType,
    normalizeRecommendationResponse: normalizeRecommendationResponse,
    buildSearchLinks: buildSearchLinks,
    getMockProducts: getMockProducts
  };
})(window);
