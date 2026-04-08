(function (window) {
  const STORAGE_KEYS = {
    gender: 'gender',
    personalColor: 'personalColor',
    resultType: 'resultType',
    surveyAnswers: 'surveyAnswers',
    surveyMeta: 'surveyMeta',
    apiBaseUrl: 'apiBaseUrl',
    profileResponse: 'profileResponse',
    recommendationResponse: 'recommendationResponse'
  };

  function $(selector, root) {
    return (root || document).querySelector(selector);
  }

  function $all(selector, root) {
    return Array.from((root || document).querySelectorAll(selector));
  }

  function getText(key, fallback) {
    const value = sessionStorage.getItem(key);
    return value === null ? (fallback === undefined ? null : fallback) : value;
  }

  function setText(key, value) {
    if (value === null || value === undefined || value === '') {
      sessionStorage.removeItem(key);
      return;
    }
    sessionStorage.setItem(key, String(value));
  }

  function getJson(key, fallback) {
    const raw = sessionStorage.getItem(key);
    if (!raw) return fallback === undefined ? null : fallback;
    try {
      return JSON.parse(raw);
    } catch (error) {
      return fallback === undefined ? null : fallback;
    }
  }

  function setJson(key, value) {
    if (value === null || value === undefined) {
      sessionStorage.removeItem(key);
      return;
    }
    sessionStorage.setItem(key, JSON.stringify(value));
  }

  function getDefaultApiBaseUrl() {
    if (window.location.protocol === 'http:' || window.location.protocol === 'https:') {
      if (window.location.port === '5500' || window.location.port === '5501') {
        return 'http://localhost:8000';
      }
      return window.location.origin;
    }
    return 'http://localhost:8000';
  }

  function getApiBaseUrl() {
    return getText(STORAGE_KEYS.apiBaseUrl, getDefaultApiBaseUrl());
  }

  function setApiBaseUrl(url) {
    setText(STORAGE_KEYS.apiBaseUrl, url);
  }

  function getAppState() {
    return {
      gender: getText(STORAGE_KEYS.gender),
      personalColor: getText(STORAGE_KEYS.personalColor),
      resultType: getText(STORAGE_KEYS.resultType),
      surveyAnswers: getJson(STORAGE_KEYS.surveyAnswers, {}),
      surveyMeta: getJson(STORAGE_KEYS.surveyMeta, {}),
      profileResponse: getJson(STORAGE_KEYS.profileResponse, null),
      recommendationResponse: getJson(STORAGE_KEYS.recommendationResponse, null)
    };
  }

  function setAppState(partialState) {
    if ('gender' in partialState) setText(STORAGE_KEYS.gender, partialState.gender);
    if ('personalColor' in partialState) setText(STORAGE_KEYS.personalColor, partialState.personalColor);
    if ('resultType' in partialState) setText(STORAGE_KEYS.resultType, partialState.resultType);
    if ('surveyAnswers' in partialState) setJson(STORAGE_KEYS.surveyAnswers, partialState.surveyAnswers);
    if ('surveyMeta' in partialState) setJson(STORAGE_KEYS.surveyMeta, partialState.surveyMeta);
    if ('profileResponse' in partialState) setJson(STORAGE_KEYS.profileResponse, partialState.profileResponse);
    if ('recommendationResponse' in partialState) setJson(STORAGE_KEYS.recommendationResponse, partialState.recommendationResponse);
  }

  function clearAppState() {
    Object.keys(STORAGE_KEYS).forEach(function (keyName) {
      sessionStorage.removeItem(STORAGE_KEYS[keyName]);
    });
  }

  function goToScreen(id) {
    $all('.screen').forEach(function (screen) {
      screen.classList.remove('active');
    });
    const target = document.getElementById(id);
    if (target) target.classList.add('active');
    window.scrollTo(0, 0);
  }

  function navigate(url) {
    window.location.href = url;
  }

  function showAlert(message) {
    window.alert(message);
  }

  function buildSpinner(targetId) {
    const target = document.getElementById(targetId);
    if (!target || target.childElementCount > 0) return;
    [
      '#FF7BAC', '#A78BFA', '#FFD93D', '#5ECFA8',
      '#FF9B6A', '#FF7BAC', '#A78BFA', '#FFD93D',
      '#5ECFA8', '#FF9B6A', '#FF7BAC', '#A78BFA',
      '#FFD93D', '#5ECFA8', '#FF9B6A', '#FF7BAC'
    ].forEach(function (color, index) {
      const span = document.createElement('span');
      span.style.cssText = 'background:' + color + ';animation-delay:' + (index * 0.075).toFixed(2) + 's';
      target.appendChild(span);
    });
  }

  function pickFirst(object, keys, fallback) {
    if (!object || typeof object !== 'object') return fallback;
    for (let index = 0; index < keys.length; index += 1) {
      const key = keys[index];
      const value = object[key];
      if (value !== undefined && value !== null && value !== '') return value;
    }
    return fallback;
  }

  function ensureArray(value) {
    if (Array.isArray(value)) return value;
    if (value === null || value === undefined) return [];
    return [value];
  }

  function escapeHtml(text) {
    return String(text)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function formatPrice(value) {
    if (value === null || value === undefined || value === '') return '';
    if (typeof value === 'number') {
      return '₩' + value.toLocaleString('ko-KR');
    }
    const numeric = Number(String(value).replace(/[^0-9.-]/g, ''));
    if (!Number.isNaN(numeric) && numeric > 0) {
      return '₩' + numeric.toLocaleString('ko-KR');
    }
    const trimmed = String(value).trim();
    return trimmed.startsWith('₩') ? trimmed : trimmed;
  }

  window.MapsiUtils = {
    STORAGE_KEYS: STORAGE_KEYS,
    $: $,
    $all: $all,
    getText: getText,
    setText: setText,
    getJson: getJson,
    setJson: setJson,
    getApiBaseUrl: getApiBaseUrl,
    setApiBaseUrl: setApiBaseUrl,
    getAppState: getAppState,
    setAppState: setAppState,
    clearAppState: clearAppState,
    goToScreen: goToScreen,
    navigate: navigate,
    showAlert: showAlert,
    buildSpinner: buildSpinner,
    pickFirst: pickFirst,
    ensureArray: ensureArray,
    escapeHtml: escapeHtml,
    formatPrice: formatPrice
  };
})(window);
