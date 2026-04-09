import { API_BASE_URL, API_PREFIX } from './constants.js';

export function buildUrl(path) {
  const normalizedPrefix = API_PREFIX ? `/${API_PREFIX.replace(/^\/+|\/+$/g, '')}` : '';
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return `${API_BASE_URL.replace(/\/$/, '')}${normalizedPrefix}${normalizedPath}`;
}

async function parseResponse(response) {
  if (response.ok) {
    const contentType = response.headers.get('content-type') || '';
    if (contentType.includes('application/json')) {
      return response.json();
    }
    return response.text();
  }

  let message = `Request failed with status ${response.status}`;
  try {
    const payload = await response.json();
    if (typeof payload.detail === 'string') message = payload.detail;
  } catch (_) {
    // noop
  }
  throw new Error(message);
}
export async function analyzeProfile(payload) {
  const response = await fetch(buildUrl('/profile'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  return parseResponse(response);
}

export async function getRecommendations(payload) {
  const response = await fetch(buildUrl('/recommendations'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  return parseResponse(response);
}

export async function crawlMusinsa(payload) {
  const response = await fetch(buildUrl('/crawl/musinsa'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  return parseResponse(response);
}

export async function crawlZigzag(payload) {
  const response = await fetch(buildUrl('/crawl/zigzag'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  return parseResponse(response);
}
