import { useState, useEffect } from "react";

// ── 데이터 정의 ──────────────────────────────────────────────────────────
const PERSONAL_COLORS = [
  { id: "spring_warm", label: "봄 웜톤", emoji: "🌸", desc: "밝고 따뜻한 복숭아·산호 계열", palette: ["#FFD580","#F4A261","#E76F51"] },
  { id: "summer_cool", label: "여름 쿨톤", emoji: "❄️", desc: "부드럽고 차가운 라벤더·로즈 계열", palette: ["#C9B8F4","#B5C7F7","#F2A7C3"] },
  { id: "autumn_warm", label: "가을 웜톤", emoji: "🍂", desc: "깊고 머스터드·카키·브라운 계열", palette: ["#C67B2A","#8B5E3C","#6B7C41"] },
  { id: "winter_cool", label: "겨울 쿨톤", emoji: "🫧", desc: "선명하고 차가운 네이비·버건디 계열", palette: ["#2C2C6C","#6D1F4E","#1A3A5C"] },
  { id: "unknown",      label: "모르겠어요", emoji: "🔍", desc: "베스트셀러 & 무채색 위주로 추천", palette: ["#3a3a3a","#888888","#cccccc"] },
];

const TPO_OPTIONS = [
  { id: "daily",    label: "데일리",     icon: "☀️", weight: 1.0 },
  { id: "work",     label: "오피스",     icon: "💼", weight: 1.0 },
  { id: "date",     label: "데이트",     icon: "🌹", weight: 1.0 },
  { id: "casual",   label: "캐주얼 외출", icon: "🎒", weight: 1.0 },
  { id: "party",    label: "파티/행사",  icon: "🥂", weight: 1.0 },
  { id: "sport",    label: "스포츠/액티브", icon: "🏃", weight: 1.0 },
  { id: "travel",   label: "여행",       icon: "✈️", weight: 1.0 },
  { id: "formal",   label: "격식/공식",  icon: "🎩", weight: 1.0 },
];

const STYLE_KEYWORDS = {
  male: [
    { id: "minimal",   label: "미니멀",   emoji: "⬜", desc: "군더더기 없는 베이직" },
    { id: "street",    label: "스트릿",   emoji: "🧢", desc: "그래픽·볼드한 스트릿" },
    { id: "classic",   label: "클래식",   emoji: "🎽", desc: "타임리스 엘레강스" },
    { id: "sporty",    label: "스포티",   emoji: "👟", desc: "기능성 + 트렌디" },
    { id: "dandy",     label: "댄디",     emoji: "🧥", desc: "정제된 젠틀맨 룩" },
    { id: "casual",    label: "캐주얼",   emoji: "👕", desc: "편안하고 자연스러운" },
  ],
  female: [
    { id: "feminine",  label: "페미닌",   emoji: "🌸", desc: "로맨틱하고 사랑스럽게" },
    { id: "minimal",   label: "미니멀",   emoji: "⬜", desc: "군더더기 없는 베이직" },
    { id: "chic",      label: "시크",     emoji: "🖤", desc: "세련되고 모던하게" },
    { id: "street",    label: "스트릿",   emoji: "🧢", desc: "볼드하고 개성 있게" },
    { id: "classic",   label: "클래식",   emoji: "👗", desc: "우아하고 품격 있게" },
    { id: "sporty",    label: "스포티",   emoji: "👟", desc: "활동적이고 트렌디하게" },
  ],
};

const AGE_GROUPS = ["10대", "20대 초반", "20대 후반", "30대", "40대", "50대+"];

// ── 추천 아이템 데이터 ──────────────────────────────────────────────────
const ITEMS = [
  // (실제 서비스에선 DB에서 가져오나, 여기선 샘플로 정의)
  { id: 1,  name: "오버사이즈 린넨 셔츠", brand: "COS",    gender: ["male","female"], color: ["spring_warm","summer_cool","unknown"],  tpo: ["daily","casual","travel"],  style: ["minimal","chic"],    price: "89,000원", img: "https://images.unsplash.com/photo-1594938298603-c8148c4b4f48?w=300&q=80" },
  { id: 2,  name: "슬림 테일러드 팬츠",   brand: "Zara",   gender: ["male","female"], color: ["winter_cool","autumn_warm","unknown"],  tpo: ["work","formal","date"],     style: ["classic","dandy","chic"], price: "79,000원", img: "https://images.unsplash.com/photo-1594938374182-a57b4e2b2b5e?w=300&q=80" },
  { id: 3,  name: "그래픽 후드 스웨트",   brand: "Supreme",gender: ["male"],          color: ["winter_cool","autumn_warm","unknown"],  tpo: ["casual","daily","sport"],   style: ["street","casual","sporty"], price: "159,000원", img: "https://images.unsplash.com/photo-1556821840-3a63f15732ce?w=300&q=80" },
  { id: 4,  name: "플로럴 미디 드레스",   brand: "& Other", gender: ["female"],        color: ["spring_warm","summer_cool","unknown"],  tpo: ["date","party","daily"],     style: ["feminine","classic"],  price: "129,000원", img: "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=300&q=80" },
  { id: 5,  name: "블랙 트렌치 코트",     brand: "Mango",  gender: ["male","female"], color: ["winter_cool","unknown"],                tpo: ["work","formal","date"],     style: ["classic","chic","minimal"], price: "199,000원", img: "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=300&q=80" },
  { id: 6,  name: "와이드 데님 팬츠",     brand: "Levi's", gender: ["male","female"], color: ["spring_warm","autumn_warm","unknown"],  tpo: ["daily","casual","travel"],  style: ["casual","street"],     price: "99,000원", img: "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=300&q=80" },
  { id: 7,  name: "리브드 터틀넥 니트",   brand: "Uniqlo", gender: ["male","female"], color: ["autumn_warm","winter_cool","unknown"],  tpo: ["daily","work","date"],      style: ["minimal","classic"],   price: "59,000원", img: "https://images.unsplash.com/photo-1608234808654-2a8875faa7fd?w=300&q=80" },
  { id: 8,  name: "카고 조거 팬츠",       brand: "Nike",   gender: ["male","female"], color: ["winter_cool","autumn_warm","unknown"],  tpo: ["sport","casual","daily"],   style: ["sporty","street"],     price: "89,000원", img: "https://images.unsplash.com/photo-1552902865-b72c031ac5ea?w=300&q=80" },
  { id: 9,  name: "새틴 슬립 드레스",     brand: "Arket",  gender: ["female"],        color: ["summer_cool","winter_cool","unknown"],  tpo: ["party","date"],             style: ["chic","feminine"],     price: "149,000원", img: "https://images.unsplash.com/photo-1623609163859-ca93c959b98a?w=300&q=80" },
  { id: 10, name: "체크 패턴 재킷",       brand: "H&M",    gender: ["male","female"], color: ["autumn_warm","unknown"],                tpo: ["work","date","formal"],     style: ["dandy","classic","chic"], price: "119,000원", img: "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=300&q=80" },
];

// ── 점수 계산 ─────────────────────────────────────────────────────────────
function calcScore(item, { gender, color, tpo, style }) {
  const colorUnknown = color === "unknown";

  const tpoMatch = tpo.reduce((acc, t) => acc + (item.tpo.includes(t) ? 1 : 0), 0) / Math.max(tpo.length, 1);
  const colorMatch = colorUnknown ? 0.5 : (item.color.includes(color) ? 1 : 0);
  const styleMatch = style.reduce((acc, s) => acc + (item.style.includes(s) ? 1 : 0), 0) / Math.max(style.length, 1);

  let score;
  if (colorUnknown) {
    score = tpoMatch * 0.55 + styleMatch * 0.45;
  } else {
    score = tpoMatch * 0.4 + colorMatch * 0.3 + styleMatch * 0.3;
  }
  const genderOk = item.gender.includes(gender);
  return genderOk ? score : 0;
}

function getReasonLabel(item, { color, tpo, style }) {
  const colorUnknown = color === "unknown";
  const tpoMatch = tpo.filter(t => item.tpo.includes(t));
  const styleMatch = style.filter(s => item.style.includes(s));
  const colorMatch = !colorUnknown && item.color.includes(color);

  const reasons = [];
  if (tpoMatch.length) reasons.push(`상황 적합도 ${colorUnknown ? "55" : "40"}% 반영`);
  if (colorMatch) reasons.push("컬러 매칭");
  if (styleMatch.length) reasons.push("스타일 취향 일치");
  if (colorUnknown && item.color.includes("unknown")) reasons.push("베스트셀러 아이템");
  return reasons.slice(0, 2).join(" · ") || "추천 아이템";
}

// ── Progress Bar ──────────────────────────────────────────────────────────
function ProgressBar({ step }) {
  const steps = ["성별 & 연령", "퍼스널 컬러", "상황 (TPO)", "선호 스타일"];
  return (
    <div style={{ marginBottom: "2rem" }}>
      <div style={{ display: "flex", alignItems: "center", gap: "0", marginBottom: "0.75rem" }}>
        {steps.map((s, i) => (
          <div key={i} style={{ display: "flex", alignItems: "center", flex: 1 }}>
            <div style={{
              width: 32, height: 32, borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center",
              background: i < step ? "var(--accent)" : i === step ? "var(--accent-soft)" : "var(--chip-bg)",
              border: i === step ? "2px solid var(--accent)" : "2px solid transparent",
              color: i <= step ? "var(--accent-text)" : "var(--muted)",
              fontSize: "0.75rem", fontWeight: 700, flexShrink: 0,
              transition: "all 0.3s ease",
            }}>
              {i < step ? "✓" : i + 1}
            </div>
            {i < steps.length - 1 && (
              <div style={{
                flex: 1, height: 2,
                background: i < step ? "var(--accent)" : "var(--border)",
                transition: "background 0.3s ease",
              }} />
            )}
          </div>
        ))}
      </div>
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        {steps.map((s, i) => (
          <div key={i} style={{
            fontSize: "0.65rem", color: i === step ? "var(--accent)" : "var(--muted)",
            fontWeight: i === step ? 700 : 400, flex: 1, textAlign: i === 0 ? "left" : i === steps.length - 1 ? "right" : "center",
            transition: "all 0.3s",
          }}>{s}</div>
        ))}
      </div>
    </div>
  );
}

// ── Chip ─────────────────────────────────────────────────────────────────
function Chip({ label, icon, selected, onClick, multi }) {
  return (
    <button onClick={onClick} style={{
      padding: "0.5rem 1rem", borderRadius: 999,
      border: selected ? "2px solid var(--accent)" : "2px solid var(--border)",
      background: selected ? "var(--accent-soft)" : "var(--chip-bg)",
      color: selected ? "var(--accent)" : "var(--text)",
      cursor: "pointer", fontSize: "0.85rem", fontWeight: selected ? 700 : 500,
      display: "flex", alignItems: "center", gap: "0.4rem",
      transition: "all 0.2s ease", fontFamily: "inherit",
      transform: selected ? "scale(1.04)" : "scale(1)",
    }}>
      {icon && <span>{icon}</span>}
      {label}
    </button>
  );
}

// ── ColorCard ─────────────────────────────────────────────────────────────
function ColorCard({ item, selected, onClick }) {
  return (
    <div onClick={onClick} style={{
      border: selected ? "2px solid var(--accent)" : "2px solid var(--border)",
      borderRadius: 16, padding: "1.25rem", cursor: "pointer", background: "var(--card-bg)",
      transition: "all 0.25s ease", transform: selected ? "translateY(-4px)" : "none",
      boxShadow: selected ? "0 8px 24px rgba(0,0,0,0.3)" : "none",
      position: "relative", overflow: "hidden",
    }}>
      {selected && (
        <div style={{
          position: "absolute", top: 10, right: 10, width: 20, height: 20,
          borderRadius: "50%", background: "var(--accent)", display: "flex", alignItems: "center",
          justifyContent: "center", fontSize: "0.7rem", color: "var(--accent-text)",
        }}>✓</div>
      )}
      <div style={{ fontSize: "2rem", marginBottom: "0.5rem" }}>{item.emoji}</div>
      <div style={{ fontWeight: 700, marginBottom: "0.25rem", fontSize: "0.95rem" }}>{item.label}</div>
      <div style={{ fontSize: "0.75rem", color: "var(--muted)", marginBottom: "0.75rem", lineHeight: 1.5 }}>{item.desc}</div>
      <div style={{ display: "flex", gap: 4 }}>
        {item.palette.map((c, i) => (
          <div key={i} style={{ width: 20, height: 20, borderRadius: "50%", background: c, border: "1px solid rgba(255,255,255,0.1)" }} />
        ))}
      </div>
    </div>
  );
}

// ── StyleCard ─────────────────────────────────────────────────────────────
function StyleCard({ item, selected, onClick }) {
  return (
    <div onClick={onClick} style={{
      border: selected ? "2px solid var(--accent)" : "2px solid var(--border)",
      borderRadius: 16, padding: "1.25rem", cursor: "pointer", background: "var(--card-bg)",
      transition: "all 0.25s ease", transform: selected ? "translateY(-4px)" : "none",
      textAlign: "center", position: "relative",
    }}>
      {selected && (
        <div style={{
          position: "absolute", top: 10, right: 10, width: 20, height: 20,
          borderRadius: "50%", background: "var(--accent)", display: "flex", alignItems: "center",
          justifyContent: "center", fontSize: "0.7rem", color: "var(--accent-text)",
        }}>✓</div>
      )}
      <div style={{ fontSize: "2.2rem", marginBottom: "0.5rem" }}>{item.emoji}</div>
      <div style={{ fontWeight: 700, marginBottom: "0.25rem" }}>{item.label}</div>
      <div style={{ fontSize: "0.75rem", color: "var(--muted)" }}>{item.desc}</div>
    </div>
  );
}

// ── ResultCard ────────────────────────────────────────────────────────────
function ResultCard({ item, score, reason, rank }) {
  const pct = Math.round(score * 100);
  const medals = ["🥇","🥈","🥉","4위","5위"];
  return (
    <div style={{
      background: "var(--card-bg)", borderRadius: 16, overflow: "hidden",
      border: rank === 0 ? "2px solid var(--accent)" : "1px solid var(--border)",
      transition: "transform 0.2s", cursor: "default",
      animation: `fadeUp 0.4s ease ${rank * 0.1}s both`,
    }}>
      <div style={{ position: "relative", height: 180, overflow: "hidden", background: "#111" }}>
        <img src={item.img} alt={item.name} style={{ width: "100%", height: "100%", objectFit: "cover", opacity: 0.85 }}
          onError={e => { e.target.style.display = "none"; }} />
        <div style={{
          position: "absolute", top: 10, left: 10,
          background: rank === 0 ? "var(--accent)" : "rgba(0,0,0,0.7)",
          color: rank === 0 ? "var(--accent-text)" : "#fff",
          borderRadius: 999, padding: "2px 10px", fontSize: "0.8rem", fontWeight: 700,
        }}>{medals[rank]}</div>
        <div style={{
          position: "absolute", top: 10, right: 10,
          background: "rgba(0,0,0,0.75)", color: "#fff",
          borderRadius: 999, padding: "2px 10px", fontSize: "0.78rem", fontWeight: 600,
        }}>매칭 {pct}%</div>
      </div>
      <div style={{ padding: "1rem" }}>
        <div style={{ fontSize: "0.7rem", color: "var(--muted)", marginBottom: "0.25rem", fontWeight: 600, textTransform: "uppercase", letterSpacing: 1 }}>{item.brand}</div>
        <div style={{ fontWeight: 700, marginBottom: "0.35rem", fontSize: "1rem" }}>{item.name}</div>
        <div style={{ fontSize: "0.75rem", color: "var(--accent)", marginBottom: "0.5rem" }}>💡 {reason}</div>
        <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: "0.6rem" }}>
          <div style={{ flex: 1, height: 4, borderRadius: 2, background: "var(--border)", overflow: "hidden" }}>
            <div style={{ height: "100%", width: `${pct}%`, background: "var(--accent)", borderRadius: 2, transition: "width 0.6s ease" }} />
          </div>
          <span style={{ fontSize: "0.75rem", color: "var(--muted)", minWidth: 32, textAlign: "right" }}>{pct}%</span>
        </div>
        <div style={{ fontWeight: 700, color: "var(--accent)", fontSize: "0.95rem" }}>{item.price}</div>
      </div>
    </div>
  );
}

// ── Reset Modal ───────────────────────────────────────────────────────────
function ResetModal({ onConfirm, onCancel }) {
  return (
    <div style={{
      position: "fixed", inset: 0, background: "rgba(0,0,0,0.75)", zIndex: 100,
      display: "flex", alignItems: "center", justifyContent: "center",
    }}>
      <div style={{
        background: "var(--card-bg)", borderRadius: 20, padding: "2rem", maxWidth: 360, width: "90%",
        border: "1px solid var(--border)", textAlign: "center",
      }}>
        <div style={{ fontSize: "2.5rem", marginBottom: "1rem" }}>🔄</div>
        <div style={{ fontWeight: 700, fontSize: "1.15rem", marginBottom: "0.5rem" }}>처음부터 다시 할까요?</div>
        <div style={{ color: "var(--muted)", fontSize: "0.875rem", marginBottom: "1.5rem" }}>
          입력한 모든 정보가 초기화됩니다.
        </div>
        <div style={{ display: "flex", gap: "0.75rem", justifyContent: "center" }}>
          <button onClick={onCancel} style={{
            padding: "0.6rem 1.5rem", borderRadius: 999, border: "1px solid var(--border)",
            background: "transparent", color: "var(--text)", cursor: "pointer", fontFamily: "inherit",
          }}>취소</button>
          <button onClick={onConfirm} style={{
            padding: "0.6rem 1.5rem", borderRadius: 999, border: "none",
            background: "var(--accent)", color: "var(--accent-text)", cursor: "pointer",
            fontWeight: 700, fontFamily: "inherit",
          }}>초기화</button>
        </div>
      </div>
    </div>
  );
}

// ── Main App ──────────────────────────────────────────────────────────────
export default function MapsiTI() {
  const [step, setStep] = useState(0);
  const [gender, setGender] = useState(null);
  const [age, setAge] = useState(null);
  const [color, setColor] = useState(null);
  const [tpo, setTpo] = useState([]);
  const [style, setStyle] = useState([]);
  const [results, setResults] = useState(null);
  const [showReset, setShowReset] = useState(false);

  const canNext = [
    gender && age,
    color,
    tpo.length > 0,
    style.length > 0,
  ][step];

  function handleNext() {
    if (step < 3) { setStep(s => s + 1); return; }
    // 결과 계산
    const scored = ITEMS
      .map(item => ({
        item,
        score: calcScore(item, { gender, color, tpo, style }),
        reason: getReasonLabel(item, { color, tpo, style }),
      }))
      .filter(x => x.score > 0)
      .sort((a, b) => b.score - a.score)
      .slice(0, 5);
    setResults(scored);
    setStep(4);
  }

  function handleReset() {
    setStep(0); setGender(null); setAge(null);
    setColor(null); setTpo([]); setStyle([]);
    setResults(null); setShowReset(false);
  }

  const toggleTpo = id => setTpo(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]);
  const toggleStyle = id => setStyle(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]);

  return (
    <div style={{ fontFamily: "'Noto Sans KR', sans-serif", minHeight: "100vh", background: "var(--bg)", color: "var(--text)" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&family=Playfair+Display:wght@700&display=swap');
        :root {
          --bg: #0d0d0f;
          --surface: #17171a;
          --card-bg: #1e1e22;
          --chip-bg: #2a2a2f;
          --border: #2e2e33;
          --text: #f0f0f0;
          --muted: #888;
          --accent: #c9a96e;
          --accent-soft: rgba(201,169,110,0.15);
          --accent-text: #0d0d0f;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        @keyframes fadeUp {
          from { opacity: 0; transform: translateY(20px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        @keyframes slideIn {
          from { opacity: 0; transform: translateX(30px); }
          to   { opacity: 1; transform: translateX(0); }
        }
        .step-content { animation: slideIn 0.35s ease; }
        button:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
        ::-webkit-scrollbar { width: 6px; } ::-webkit-scrollbar-track { background: var(--bg); }
        ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
      `}</style>

      {/* Header */}
      <header style={{
        position: "sticky", top: 0, zIndex: 50,
        background: "rgba(13,13,15,0.85)", backdropFilter: "blur(12px)",
        borderBottom: "1px solid var(--border)",
        padding: "0 1.5rem", height: 60,
        display: "flex", alignItems: "center", justifyContent: "space-between",
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
          <span style={{ fontSize: "1.3rem" }}>🧪</span>
          <span style={{ fontFamily: "'Playfair Display', serif", fontSize: "1.2rem", fontWeight: 700, color: "var(--accent)" }}>Mapsi-TI</span>
          <span style={{ fontSize: "0.7rem", color: "var(--muted)", fontWeight: 500, marginLeft: 4 }}>AI 퍼스널 스타일 큐레이션</span>
        </div>
        <button onClick={() => setShowReset(true)} style={{
          background: "transparent", border: "1px solid var(--border)", borderRadius: 999,
          color: "var(--muted)", padding: "0.35rem 0.9rem", cursor: "pointer",
          fontSize: "0.78rem", display: "flex", alignItems: "center", gap: 5, fontFamily: "inherit",
          transition: "all 0.2s",
        }}
          onMouseEnter={e => { e.target.style.color = "var(--text)"; e.target.style.borderColor = "var(--text)"; }}
          onMouseLeave={e => { e.target.style.color = "var(--muted)"; e.target.style.borderColor = "var(--border)"; }}
        >
          <span>↺</span> 초기화
        </button>
      </header>

      <main style={{ maxWidth: 720, margin: "0 auto", padding: "2rem 1.5rem 6rem" }}>
        {step < 4 && <ProgressBar step={step} />}

        {/* ─── Step 0: 성별 & 연령 ─── */}
        {step === 0 && (
          <div className="step-content">
            <h2 style={{ fontSize: "1.5rem", fontWeight: 900, marginBottom: 0.5 }}>성별을 선택해주세요</h2>
            <p style={{ color: "var(--muted)", fontSize: "0.875rem", marginBottom: "1.5rem" }}>성별에 따라 추천 아이템이 달라져요</p>
            <div style={{ display: "flex", gap: "1rem", marginBottom: "2.5rem" }}>
              {[{ id:"male", label:"남성", emoji:"👔" }, { id:"female", label:"여성", emoji:"👗" }].map(g => (
                <div key={g.id} onClick={() => setGender(g.id)} style={{
                  flex: 1, border: gender === g.id ? "2px solid var(--accent)" : "2px solid var(--border)",
                  borderRadius: 20, padding: "2rem 1rem", textAlign: "center", cursor: "pointer",
                  background: gender === g.id ? "var(--accent-soft)" : "var(--card-bg)",
                  transform: gender === g.id ? "scale(1.03)" : "scale(1)",
                  transition: "all 0.25s ease",
                }}>
                  <div style={{ fontSize: "3rem", marginBottom: "0.5rem" }}>{g.emoji}</div>
                  <div style={{ fontWeight: 700, fontSize: "1.05rem", color: gender === g.id ? "var(--accent)" : "var(--text)" }}>{g.label}</div>
                </div>
              ))}
            </div>

            <h3 style={{ fontWeight: 700, marginBottom: "1rem", fontSize: "1.05rem" }}>연령대를 선택해주세요</h3>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "0.6rem" }}>
              {AGE_GROUPS.map(a => (
                <Chip key={a} label={a} selected={age === a} onClick={() => setAge(a)} />
              ))}
            </div>
          </div>
        )}

        {/* ─── Step 1: 퍼스널 컬러 ─── */}
        {step === 1 && (
          <div className="step-content">
            <h2 style={{ fontSize: "1.5rem", fontWeight: 900, marginBottom: 0 }}>나의 퍼스널 컬러는?</h2>
            <p style={{ color: "var(--muted)", fontSize: "0.875rem", marginBottom: "1.5rem" }}>모르셔도 괜찮아요! '모르겠어요'를 선택하세요 🔍</p>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(160px, 1fr))", gap: "0.85rem" }}>
              {PERSONAL_COLORS.map(c => (
                <ColorCard key={c.id} item={c} selected={color === c.id} onClick={() => setColor(c.id)} />
              ))}
            </div>
          </div>
        )}

        {/* ─── Step 2: TPO 다중 선택 ─── */}
        {step === 2 && (
          <div className="step-content">
            <h2 style={{ fontSize: "1.5rem", fontWeight: 900, marginBottom: 0 }}>어떤 상황을 위한 스타일인가요?</h2>
            <p style={{ color: "var(--muted)", fontSize: "0.875rem", marginBottom: "1.5rem" }}>여러 개 선택 가능해요 (추천 점수에 40~55% 반영)</p>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "0.6rem" }}>
              {TPO_OPTIONS.map(t => (
                <Chip key={t.id} label={t.label} icon={t.icon} selected={tpo.includes(t.id)} onClick={() => toggleTpo(t.id)} multi />
              ))}
            </div>
            {tpo.length > 0 && (
              <p style={{ marginTop: "1rem", fontSize: "0.8rem", color: "var(--accent)" }}>
                ✓ {tpo.length}개 선택됨
              </p>
            )}
          </div>
        )}

        {/* ─── Step 3: 선호 스타일 ─── */}
        {step === 3 && (
          <div className="step-content">
            <h2 style={{ fontSize: "1.5rem", fontWeight: 900, marginBottom: 0 }}>선호하는 스타일을 골라주세요</h2>
            <p style={{ color: "var(--muted)", fontSize: "0.875rem", marginBottom: "1.5rem" }}>여러 개 선택 가능해요</p>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(145px, 1fr))", gap: "0.85rem" }}>
              {(STYLE_KEYWORDS[gender] || STYLE_KEYWORDS.male).map(s => (
                <StyleCard key={s.id} item={s} selected={style.includes(s.id)} onClick={() => toggleStyle(s.id)} />
              ))}
            </div>
          </div>
        )}

        {/* ─── Step 4: 결과 ─── */}
        {step === 4 && results && (
          <div className="step-content">
            <div style={{ textAlign: "center", marginBottom: "2.5rem" }}>
              <div style={{ fontSize: "3rem", marginBottom: "0.5rem" }}>✨</div>
              <h2 style={{ fontFamily: "'Playfair Display', serif", fontSize: "1.8rem", fontWeight: 700, color: "var(--accent)", marginBottom: "0.5rem" }}>
                나의 추천 스타일
              </h2>
              <p style={{ color: "var(--muted)", fontSize: "0.875rem" }}>
                {color === "unknown" ? "상황 55% + 스타일 45% 기반" : "상황 40% + 퍼스널 컬러 30% + 스타일 30% 기반"} 추천
              </p>
            </div>

            {/* Summary pills */}
            <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", justifyContent: "center", marginBottom: "2rem" }}>
              {[
                gender === "male" ? "👔 남성" : "👗 여성",
                age,
                PERSONAL_COLORS.find(c => c.id === color)?.label,
                ...tpo.slice(0,2).map(t => TPO_OPTIONS.find(x => x.id === t)?.label),
              ].filter(Boolean).map((pill, i) => (
                <span key={i} style={{
                  padding: "0.3rem 0.8rem", borderRadius: 999,
                  background: "var(--accent-soft)", color: "var(--accent)",
                  fontSize: "0.78rem", fontWeight: 600,
                }}>{pill}</span>
              ))}
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: "1rem" }}>
              {results.map(({ item, score, reason }, i) => (
                <ResultCard key={item.id} item={item} score={score} reason={reason} rank={i} />
              ))}
            </div>

            <div style={{ textAlign: "center", marginTop: "3rem" }}>
              <button onClick={handleReset} style={{
                padding: "0.85rem 2.5rem", borderRadius: 999, border: "2px solid var(--accent)",
                background: "transparent", color: "var(--accent)", cursor: "pointer",
                fontWeight: 700, fontSize: "1rem", fontFamily: "inherit", transition: "all 0.2s",
              }}
                onMouseEnter={e => { e.currentTarget.style.background = "var(--accent)"; e.currentTarget.style.color = "var(--accent-text)"; }}
                onMouseLeave={e => { e.currentTarget.style.background = "transparent"; e.currentTarget.style.color = "var(--accent)"; }}
              >
                다시 테스트하기
              </button>
            </div>
          </div>
        )}

        {/* ─── Footer Nav ─── */}
        {step < 4 && (
          <div style={{
            position: "fixed", bottom: 0, left: 0, right: 0,
            background: "rgba(13,13,15,0.95)", backdropFilter: "blur(12px)",
            borderTop: "1px solid var(--border)",
            padding: "1rem 1.5rem",
            display: "flex", alignItems: "center", justifyContent: "space-between",
            maxWidth: 720, margin: "0 auto",
          }}>
            <div style={{ position: "fixed", bottom: 0, left: 0, right: 0, background: "rgba(13,13,15,0.95)", backdropFilter: "blur(12px)", borderTop: "1px solid var(--border)", padding: "1rem 1.5rem", display: "flex", alignItems: "center", justifyContent: "space-between", zIndex: 40 }}>
              <button onClick={() => setStep(s => s - 1)} disabled={step === 0} style={{
                padding: "0.75rem 1.5rem", borderRadius: 999,
                border: "1px solid var(--border)", background: "transparent",
                color: step === 0 ? "var(--border)" : "var(--text)",
                cursor: step === 0 ? "not-allowed" : "pointer",
                fontFamily: "inherit", fontWeight: 600, fontSize: "0.9rem", transition: "all 0.2s",
              }}>← 이전</button>

              <span style={{ fontSize: "0.8rem", color: "var(--muted)" }}>{step + 1} / 4</span>

              <button onClick={handleNext} disabled={!canNext} style={{
                padding: "0.75rem 2rem", borderRadius: 999,
                border: "none",
                background: canNext ? "var(--accent)" : "var(--chip-bg)",
                color: canNext ? "var(--accent-text)" : "var(--muted)",
                cursor: canNext ? "pointer" : "not-allowed",
                fontFamily: "inherit", fontWeight: 700, fontSize: "0.9rem", transition: "all 0.2s",
              }}>
                {step === 3 ? "✨ 결과 분석" : "다음 →"}
              </button>
            </div>
          </div>
        )}
      </main>

      {showReset && <ResetModal onConfirm={handleReset} onCancel={() => setShowReset(false)} />}
    </div>
  );
}
