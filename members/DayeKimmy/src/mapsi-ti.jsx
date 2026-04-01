<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Mapsi-TI · AI 퍼스널 스타일 큐레이션</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&family=Cormorant+Garamond:wght@600;700&display=swap" rel="stylesheet" />
  <style>
    /* ── Reset & Variables ─────────────────────────────────── */
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --bg:          #0b0b0e;
      --surface:     #13131a;
      --card:        #1a1a24;
      --card-hover:  #20202c;
      --border:      rgba(255,255,255,0.08);
      --border-sel:  rgba(255,255,255,0.25);
      --text:        #efefef;
      --muted:        #888;
      --gold:        #c9a96e;
      --gold-soft:   rgba(201,169,110,0.12);
      --gold-glow:   rgba(201,169,110,0.3);
      --radius:      14px;
    }

    html { scroll-behavior: smooth; }

    body {
      font-family: 'Noto Sans KR', sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      line-height: 1.6;
    }

    body::before {
      content: '';
      position: fixed; inset: 0; z-index: 0; pointer-events: none;
      background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.035'/%3E%3C/svg%3E");
      opacity: 0.4;
    }

    /* ── Header ────────────────────────────────────────────── */
    header {
      position: sticky; top: 0; z-index: 100;
      background: rgba(11,11,14,0.88);
      backdrop-filter: blur(16px);
      border-bottom: 1px solid var(--border);
      padding: 0 2rem;
      height: 60px;
      display: flex; align-items: center; justify-content: space-between;
    }

    .logo {
      display: flex; align-items: center; gap: 0.5rem;
      text-decoration: none;
    }
    .logo-icon { font-size: 1.2rem; }
    .logo-name {
      font-family: 'Cormorant Garamond', serif;
      font-size: 1.3rem; font-weight: 700;
      color: var(--gold); letter-spacing: 0.03em;
    }
    .logo-sub {
      font-size: 0.65rem; color: var(--muted);
      font-weight: 500; letter-spacing: 0.02em;
    }

    .badge {
      background: var(--gold-soft);
      color: var(--gold);
      border: 1px solid rgba(201,169,110,0.3);
      border-radius: 999px;
      padding: 0.3rem 0.85rem;
      font-size: 0.72rem; font-weight: 700;
      letter-spacing: 0.08em; text-transform: uppercase;
    }

    /* ── Layout ────────────────────────────────────────────── */
    .wrapper {
      position: relative; z-index: 1;
      max-width: 780px; margin: 0 auto;
      padding: 3rem 1.5rem 8rem;
    }

    /* ── Section Header ────────────────────────────────────── */
    .section-num {
      font-size: 0.7rem; font-weight: 700;
      color: var(--gold); letter-spacing: 0.15em; text-transform: uppercase;
      margin-bottom: 0.4rem;
    }
    .section-title {
      font-size: 1.6rem; font-weight: 900;
      margin-bottom: 0.35rem; line-height: 1.25;
    }
    .section-desc {
      font-size: 0.82rem; color: var(--muted); margin-bottom: 1.75rem;
    }

    .divider {
      height: 1px; background: var(--border);
      margin: 3rem 0;
    }

    /* ── Gender Buttons ────────────────────────────────────── */
    .gender-group {
      display: grid; grid-template-columns: 1fr 1fr;
      gap: 1rem; margin-bottom: 0.5rem;
    }

    .gender-btn {
      position: relative;
      padding: 2.2rem 1rem;
      border-radius: var(--radius);
      border: 1.5px solid var(--border);
      background: var(--card);
      cursor: pointer; text-align: center;
      transition: all 0.25s ease;
      user-select: none;
    }
    .gender-btn:hover {
      border-color: var(--border-sel);
      background: var(--card-hover);
      transform: translateY(-2px);
    }
    .gender-btn.selected {
      border-color: var(--gold);
      background: var(--gold-soft);
      box-shadow: 0 0 0 1px var(--gold), 0 8px 28px var(--gold-glow);
      transform: translateY(-3px);
    }
    .gender-btn .g-emoji { font-size: 2.6rem; display: block; margin-bottom: 0.5rem; }
    .gender-btn .g-label { font-size: 1rem; font-weight: 700; }
    .gender-btn.selected .g-label { color: var(--gold); }
    .check-badge {
      position: absolute; top: 10px; right: 10px;
      width: 22px; height: 22px; border-radius: 50%;
      background: var(--gold); color: #0b0b0e;
      font-size: 0.7rem; font-weight: 900;
      display: flex; align-items: center; justify-content: center;
      opacity: 0; transform: scale(0.5);
      transition: all 0.2s ease;
    }
    .gender-btn.selected .check-badge { opacity: 1; transform: scale(1); }

    /* ── Personal Color Grid ───────────────────────────────── */
    .color-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(170px, 1fr));
      gap: 0.85rem;
    }

    .color-card {
      position: relative;
      padding: 1.25rem;
      border-radius: var(--radius);
      border: 1.5px solid var(--border);
      background: var(--card);
      cursor: pointer;
      transition: all 0.25s ease;
      user-select: none;
      overflow: hidden;
    }
    .color-card:hover {
      border-color: var(--border-sel);
      background: var(--card-hover);
      transform: translateY(-3px);
    }
    .color-card.selected {
      border-color: var(--gold);
      box-shadow: 0 0 0 1px var(--gold), 0 6px 24px rgba(0,0,0,0.4);
      transform: translateY(-4px);
    }

    .color-card .season-stripe {
      position: absolute; top: 0; left: 0; right: 0; height: 3px;
      border-radius: var(--radius) var(--radius) 0 0;
    }

    .color-card .cc-season {
      font-size: 0.62rem; font-weight: 700;
      letter-spacing: 0.12em; text-transform: uppercase;
      margin-bottom: 0.45rem; opacity: 0.75;
    }
    .color-card .cc-name {
      font-size: 0.92rem; font-weight: 700;
      margin-bottom: 0.3rem;
    }
    .color-card .cc-desc {
      font-size: 0.7rem; color: var(--muted);
      line-height: 1.45; margin-bottom: 0.75rem;
    }
    .cc-palette { display: flex; gap: 4px; }
    .cc-swatch {
      width: 18px; height: 18px; border-radius: 50%;
      border: 1.5px solid rgba(255,255,255,0.12);
      flex-shrink: 0;
    }
    .color-card .cc-check {
      position: absolute; top: 10px; right: 10px;
      width: 20px; height: 20px; border-radius: 50%;
      background: var(--gold); color: #0b0b0e;
      font-size: 0.65rem; font-weight: 900;
      display: flex; align-items: center; justify-content: center;
      opacity: 0; transform: scale(0.5); transition: all 0.2s;
    }
    .color-card.selected .cc-check { opacity: 1; transform: scale(1); }

    .s-spring { color: #f4a261; }
    .s-summer { color: #90bfff; }
    .s-autumn { color: #c67b2a; }
    .s-winter { color: #8ec5fc; }
    .stripe-spring { background: linear-gradient(90deg,#ffd580,#f4a261,#e76f51); }
    .stripe-summer { background: linear-gradient(90deg,#c9b8f4,#90bfff,#f2a7c3); }
    .stripe-autumn { background: linear-gradient(90deg,#c67b2a,#8b5e3c,#6b7c41); }
    .stripe-winter { background: linear-gradient(90deg,#8ec5fc,#6d1f4e,#2c2c6c); }
    .stripe-unknown { background: linear-gradient(90deg,#555,#888,#bbb); }

    /* ── Summary Bar ───────────────────────────────────────── */
    .summary-bar {
      position: fixed; bottom: 0; left: 0; right: 0; z-index: 100;
      background: rgba(11,11,14,0.94);
      backdrop-filter: blur(16px);
      border-top: 1px solid var(--border);
      padding: 1rem 2rem;
      display: flex; align-items: center; justify-content: space-between;
      gap: 1rem;
    }

    .summary-pills { display: flex; flex-wrap: wrap; gap: 0.4rem; flex: 1; }
    .s-pill {
      padding: 0.25rem 0.7rem;
      border-radius: 999px;
      background: rgba(255,255,255,0.05);
      color: var(--muted);
      font-size: 0.72rem; font-weight: 600;
      border: 1px solid var(--border);
      transition: all 0.2s;
    }
    .s-pill.filled {
      background: var(--gold-soft);
      color: var(--gold);
      border-color: rgba(201,169,110,0.3);
    }

    .next-btn {
      padding: 0.75rem 2rem;
      border-radius: 999px; border: none;
      background: var(--gold);
      color: #0b0b0e;
      font-family: inherit; font-size: 0.9rem; font-weight: 700;
      cursor: pointer; white-space: nowrap;
      transition: all 0.25s ease;
      box-shadow: 0 4px 20px var(--gold-glow);
    }
    .next-btn:disabled {
      background: #2a2a2f; color: #555;
      cursor: not-allowed; box-shadow: none;
    }
    .next-btn:not(:disabled):hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 28px var(--gold-glow);
    }

    @keyframes fadeUp {
      from { opacity: 0; transform: translateY(18px); }
      to   { opacity: 1; transform: translateY(0); }
    }
    .section-block { animation: fadeUp 0.5s ease both; }

    .step-label {
      display: inline-flex; align-items: center; gap: 0.5rem;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 999px;
      padding: 0.35rem 1rem;
      font-size: 0.72rem; font-weight: 700;
      color: var(--muted);
      letter-spacing: 0.05em; text-transform: uppercase;
      margin-bottom: 1.25rem;
    }
    .step-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--gold); }

    @media (max-width: 560px) {
      .color-grid { grid-template-columns: repeat(2, 1fr); }
      .summary-bar { flex-direction: column; align-items: stretch; }
      .next-btn { width: 100%; text-align: center; }
    }
  </style>
</head>
<body>

<header>
  <a class="logo" href="#">
    <span class="logo-icon">🧪</span>
    <span class="logo-name">Mapsi-TI</span>
    <span class="logo-sub">AI 퍼스널 스타일 큐레이션</span>
  </a>
  <span class="badge">Step 1 of 2</span>
</header>

<main class="wrapper">

  <section class="section-block" id="sec-gender">
    <div class="step-label"><span class="step-dot"></span>Section 01</div>
    <div class="section-num">Gender</div>
    <h2 class="section-title">성별을 알려주세요</h2>
    <p class="section-desc">선택한 성별에 따라 추천 아이템이 필터링됩니다.</p>

    <div class="gender-group" id="gender-group">
      <div class="gender-btn" data-val="male" onclick="selectGender(this)">
        <span class="check-badge">✓</span>
        <span class="g-emoji">👔</span>
        <span class="g-label">남성</span>
      </div>
      <div class="gender-btn" data-val="female" onclick="selectGender(this)">
        <span class="check-badge">✓</span>
        <span class="g-emoji">👗</span>
        <span class="g-label">여성</span>
      </div>
    </div>
  </section>

  <div class="divider"></div>

  <section class="section-block" id="sec-color">
    <div class="step-label"><span class="step-dot"></span>Section 02</div>
    <div class="section-num">Personal Color · 12 Tones</div>
    <h2 class="section-title">나의 퍼스널 컬러는?</h2>
    <p class="section-desc">진단을 받으셨다면 해당 톤을, 모르신다면 맨 아래 '모르겠어요'를 선택해주세요.</p>

    <div class="color-grid" id="color-grid">
      <div class="color-card" data-val="spring_light" onclick="selectColor(this)">
        <div class="season-stripe stripe-spring"></div>
        <span class="cc-check">✓</span>
        <div class="cc-season s-spring">🌸 봄</div>
        <div class="cc-name">라이트 봄</div>
        <div class="cc-desc">밝고 연한 파스텔 계열. 부드럽고 산뜻한 이미지.</div>
        <div class="cc-palette">
          <div class="cc-swatch" style="background:#FFD9B3;"></div>
          <div class="cc-swatch" style="background:#FFC3A0;"></div>
          <div class="cc-swatch" style="background:#FFEAD5;"></div>
          <div class="cc-swatch" style="background:#FBE4C4;"></div>
        </div>
      </div>
      <div class="color-card" data-val="spring_bright" onclick="selectColor(this)">
        <div class="season-stripe stripe-spring"></div>
        <span class="cc-check">✓</span>
        <div class="cc-season s-spring">🌸 봄</div>
        <div class="cc-name">브라이트 봄</div>
        <div class="cc-desc">선명하고 생기 있는 비비드한 봄 톤.</div>
        <div class="cc-palette">
          <div class="cc-swatch" style="background:#FF9F43;"></div>
          <div class="cc-swatch" style="background:#FFD32A;"></div>
          <div class="cc-swatch" style="background:#FF6B6B;"></div>
          <div class="cc-swatch" style="background:#FFA502;"></div>
        </div>
      </div>
      <div class="color-card" data-val="spring_warm" onclick="selectColor(this)">
        <div class="season-stripe stripe-spring"></div>
        <span class="cc-check">✓</span>
        <div class="cc-season s-spring">🌸 봄</div>
        <div class="cc-name">웜 봄</div>
        <div class="cc-desc">따뜻한 복숭아·살구 베이스. 건강한 피부톤.</div>
        <div class="cc-palette">
          <div class="cc-swatch" style="background:#F4A261;"></div>
          <div class="cc-swatch" style="background:#E76F51;"></div>
          <div class="cc-swatch" style="background:#FFBA93;"></div>
          <div class="cc-swatch" style="background:#E8956D;"></div>
        </div>
      </div>

      <div class="color-card" data-val="summer_light" onclick="selectColor(this)">
        <div class="season-stripe stripe-summer"></div>
        <span class="cc-check">✓</span>
        <div class="cc-season s-summer">❄️ 여름</div>
        <div class="cc-name">라이트 여름</div>
        <div class="cc-desc">연하고 차가운 파스텔. 청순하고 부드러운 이미지.</div>
        <div class="cc-palette">
          <div class="cc-swatch" style="background:#B5D5F7;"></div>
          <div class="cc-swatch" style="background:#D9C4F0;"></div>
          <div class="cc-swatch" style="background:#C8E6F5;"></div>
          <div class="cc-swatch" style="background:#F2C4D0;"></div>
        </div>
      </div>
      <div class="color-card" data-val="summer_bright" onclick="selectColor(this)">
        <div class="season-stripe stripe-summer"></div>
        <span class="cc-check">✓</span>
        <div class="cc-season s-summer">❄️ 여름</div>
        <div class="cc-name">브라이트 여름</div>
        <div class="cc-desc">밝고 선명한 쿨 계열. 생동감 있는 쿨톤.</div>
        <div class="cc-palette">
          <div class="cc-swatch" style="background:#74B9FF;"></div>
          <div class="cc-swatch" style="background:#A29BFE;"></div>
          <div class="cc-swatch" style="background:#FD79A8;"></div>
          <div class="cc-swatch" style="background:#55EFC4;"></div>
        </div>
      </div>
      <div class="color-card" data-val="summer_muted" onclick="selectColor(this)">
        <div class="season-stripe stripe-summer"></div>
        <span class="cc-check">✓</span>
        <div class="cc-season s-summer">❄️ 여름</div>
        <div class="cc-name">뮤트 여름</div>
        <div class="cc-desc">채도를 낮춘 차분한 쿨 계열. 세련되고 은은한 느낌.</div>
        <div class="cc-palette">
          <div class="cc-swatch" style="background:#9BB5CC;"></div>
          <div class="cc-swatch" style="background:#B0A4C8;"></div>
          <div class="cc-swatch" style="background:#C4B3C9;"></div>
          <div class="cc-swatch" style="background:#8FA9BE;"></div>
        </div>
      </div>

      <div class="color-card" data-val="autumn_warm" onclick="selectColor(this)">
        <div class="season-stripe stripe-autumn"></div>
        <span class="cc-check">✓</span>
        <div class="cc-season s-autumn">🍂 가을</div>
        <div class="cc-name">웜 가을</div>
        <div class="cc-desc">따뜻한 카멜·테라코타. 클래식하고 여유로운 분위기.</div>
        <div class="cc-palette">
          <div class="cc-swatch" style="background:#C67B2A;"></div>
          <div class="cc-swatch" style="background:#D4956A;"></div>
          <div class="cc-swatch" style="background:#E8B07A;"></div>
          <div class="cc-swatch" style="background:#A8673B;"></div>
        </div>
      </div>
      <div class="color-card" data-val="autumn_deep" onclick="selectColor(this)">
        <div class="season-stripe stripe-autumn"></div>
        <span class="cc-check">✓</span>
        <div class="cc-season s-autumn">🍂 가을</div>
        <div class="cc-name">딥 가을</div>
        <div class="cc-desc">깊고 진한 버건디·브라운. 성숙하고 무게감 있는 룩.</div>
        <div class="cc-palette">
          <div class="cc-swatch" style="background:#8B3A3A;"></div>
          <div class="cc-swatch" style="background:#5C3317;"></div>
          <div class="cc-swatch" style="background:#7B4F2E;"></div>
          <div class="cc-swatch" style="background:#A0522D;"></div>
        </div>
      </div>
      <div class="color-card" data-val="autumn_muted" onclick="selectColor(this)">
        <div class="season-stripe stripe-autumn"></div>
        <span class="cc-check">✓</span>
        <div class="cc-season s-autumn">🍂 가을</div>
        <div class="cc-name">뮤트 가을</div>
        <div class="cc-desc">채도 낮은 카키·올리브. 내추럴하고 어스톤 스타일.</div>
        <div class="cc-palette">
          <div class="cc-swatch" style="background:#8D8B4E;"></div>
          <div class="cc-swatch" style="background:#6B7C41;"></div>
          <div class="cc-swatch" style="background:#9C8B5E;"></div>
          <div class="cc-swatch" style="background:#7A7253;"></div>
        </div>
      </div>

      <div class="color-card" data-val="winter_bright" onclick="selectColor(this)">
        <div class="season-stripe stripe-winter"></div>
        <span class="cc-check">✓</span>
        <div class="cc-season s-winter">🫧 겨울</div>
        <div class="cc-name">브라이트 겨울</div>
        <div class="cc-desc">선명하고 청량한 아이시 컬러. 도회적이고 강렬한 인상.</div>
        <div class="cc-palette">
          <div class="cc-swatch" style="background:#00CEC9;"></div>
          <div class="cc-swatch" style="background:#6C5CE7;"></div>
          <div class="cc-swatch" style="background:#E84393;"></div>
          <div class="cc-swatch" style="background:#0984E3;"></div>
        </div>
      </div>
      <div class="color-card" data-val="winter_deep" onclick="selectColor(this)">
        <div class="season-stripe stripe-winter"></div>
        <span class="cc-check">✓</span>
        <div class="cc-season s-winter">🫧 겨울</div>
        <div class="cc-name">딥 겨울</div>
        <div class="cc-desc">짙은 네이비·블랙·버건디. 다크하고 카리스마 있는 스타일.</div>
        <div class="cc-palette">
          <div class="cc-swatch" style="background:#2C2C6C;"></div>
          <div class="cc-swatch" style="background:#6D1F4E;"></div>
          <div class="cc-swatch" style="background:#1A1A3A;"></div>
          <div class="cc-swatch" style="background:#0D3349;"></div>
        </div>
      </div>
      <div class="color-card" data-val="winter_cool" onclick="selectColor(this)">
        <div class="season-stripe stripe-winter"></div>
        <span class="cc-check">✓</span>
        <div class="cc-season s-winter">🫧 겨울</div>
        <div class="cc-name">쿨 겨울</div>
        <div class="cc-desc">차가운 핑크·라일락. 청순하면서도 모던한 쿨톤.</div>
        <div class="cc-palette">
          <div class="cc-swatch" style="background:#8EC5FC;"></div>
          <div class="cc-swatch" style="background:#C9B4F7;"></div>
          <div class="cc-swatch" style="background:#F5BFDF;"></div>
          <div class="cc-swatch" style="background:#A8D8EA;"></div>
        </div>
      </div>

      <div class="color-card" data-val="unknown" onclick="selectColor(this)"
           style="grid-column: 1 / -1; display:flex; align-items:center; gap:1.25rem; padding:1.1rem 1.4rem;">
        <div class="season-stripe stripe-unknown"></div>
        <span class="cc-check">✓</span>
        <div style="font-size:2rem;">🔍</div>
        <div>
          <div class="cc-name" style="margin-bottom:0.2rem;">모르겠어요</div>
          <div class="cc-desc" style="margin-bottom:0.5rem;">진단 전이라도 괜찮아요. 베스트셀러 & 무채색 위주로 추천해드립니다.</div>
          <div class="cc-palette">
            <div class="cc-swatch" style="background:#222;"></div>
            <div class="cc-swatch" style="background:#555;"></div>
            <div class="cc-swatch" style="background:#888;"></div>
            <div class="cc-swatch" style="background:#bbb;"></div>
          </div>
        </div>
      </div>
    </div>
  </section>

</main>

<div class="summary-bar">
  <div class="summary-pills" id="summary-pills">
    <span class="s-pill" id="pill-gender">성별</span>
    <span class="s-pill" id="pill-color">퍼스널 컬러</span>
  </div>
  <button class="next-btn" id="next-btn" disabled onclick="handleNext()">
    2단계로 →
  </button>
</div>

<script>
  // 연령대와 TPO를 제외한 상태값
  const state = { gender: null, color: null };

  const colorLabels = {
    spring_light:"라이트 봄", spring_bright:"브라이트 봄", spring_warm:"웜 봄",
    summer_light:"라이트 여름", summer_bright:"브라이트 여름", summer_muted:"뮤트 여름",
    autumn_warm:"웜 가을", autumn_deep:"딥 가을", autumn_muted:"뮤트 가을",
    winter_bright:"브라이트 겨울", winter_deep:"딥 겨울", winter_cool:"쿨 겨울",
    unknown:"모르겠어요"
  };

  function selectGender(el) {
    document.querySelectorAll('.gender-btn').forEach(b => b.classList.remove('selected'));
    el.classList.add('selected');
    state.gender = el.dataset.val;
    updateUI();
  }

  function selectColor(el) {
    document.querySelectorAll('.color-card').forEach(c => c.classList.remove('selected'));
    el.classList.add('selected');
    state.color = el.dataset.val;
    updateUI();
  }

  function updateUI() {
    const pg  = document.getElementById('pill-gender');
    const pc  = document.getElementById('pill-color');
    const btn = document.getElementById('next-btn');

    pg.textContent = state.gender ? (state.gender === 'male' ? '👔 남성' : '👗 여성') : '성별';
    pg.className = 's-pill' + (state.gender ? ' filled' : '');

    pc.textContent = state.color ? colorLabels[state.color] : '퍼스널 컬러';
    pc.className = 's-pill' + (state.color ? ' filled' : '');

    // 성별과 컬러가 모두 선택되었을 때 버튼 활성화
    btn.disabled = !(state.gender && state.color);
  }

  function handleNext() {
    console.log('Step 1 완료 — State:', JSON.stringify(state, null, 2));
    alert(`Step 1 완료!\n\n성별: ${state.gender === 'male' ? '남성' : '여성'}\n퍼스널 컬러: ${colorLabels[state.color]}\n\n→ 2단계로 이동합니다.`);
  }
</script>
</body>
</html>