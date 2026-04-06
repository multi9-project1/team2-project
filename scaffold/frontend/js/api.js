async function fetchPersonaResult(payload) {
  try {
    const response = await fetch('/profile', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) throw new Error('API response error');
    return await response.json();
  } catch (error) {
    return { ok: false, fallback: true };
  }
}

async function fetchProducts(payload) {
  try {
    const response = await fetch('/recommendations', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) throw new Error('API response error');
    return await response.json();
  } catch (error) {
    const { fit, color, category, gender } = payload;
    const musinsa = [
      { brand: '무신사 스탠다드', name: `${color} ${fit} ${category}`, price: '29,900', emoji: '👔', bg: '#DBEAFE' },
      { brand: '커버낫', name: `베이직 ${category} (${fit})`, price: '49,000', emoji: '👖', bg: '#EDE9FE' },
      { brand: '디스이즈네버댓', name: `${color} 로고 ${category}`, price: '79,000', emoji: '👕', bg: '#D1FAE5' },
      { brand: '아더에러', name: `크롭 ${category} ${fit}`, price: '129,000', emoji: '🧥', bg: '#FEF3C7' },
      { brand: '마르디 메크르디', name: `${color} 포인트 ${category}`, price: '59,000', emoji: '🌸', bg: '#FCE7F3' }
    ];

    const zigzag = gender === 'W'
      ? [
          { brand: '지그재그PICK', name: `${color} ${fit} ${category}`, price: '35,000', emoji: '👗', bg: '#FDF2F8' },
          { brand: '스타일난다', name: `트렌디 ${category} (${color})`, price: '28,000', emoji: '👘', bg: '#EDE9FE' },
          { brand: '하프클럽', name: `${fit} 니트 ${category}`, price: '42,000', emoji: '🧶', bg: '#FEF3C7' },
          { brand: '온더플라이', name: `${color} 와이드 ${category}`, price: '38,000', emoji: '👚', bg: '#D1FAE5' },
          { brand: '에이블리', name: `데님 ${fit} ${category}`, price: '55,000', emoji: '🎽', bg: '#DBEAFE' }
        ]
      : [];

    return {
      ok: true,
      fallback: true,
      musinsa,
      zigzag,
      links: {
        musinsa: `https://www.musinsa.com/search/goods?keyword=${encodeURIComponent(`${fit} ${color} ${getGenderLabel(gender)} ${category}`)}&gf=${gender === 'W' ? 'F' : 'M'}`,
        zigzag: `https://zigzag.kr/search?keyword=${encodeURIComponent(`${fit} ${color} ${category}`)}`
      }
    };
  }
}