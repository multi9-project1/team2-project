export const API_BASE_URL = 'http://127.0.0.1:8000';
export const API_PREFIX = '';

export const PERSONAL_COLOR_LABELS = {
  spring_light: '봄 라이트',
  spring_bright: '봄 브라이트',
  spring_warm: '봄 웜',
  autumn_muted: '가을 뮤트',
  autumn_deep: '가을 딥',
  autumn_warm: '가을 웜',
  summer_light: '여름 라이트',
  summer_muted: '여름 뮤트',
  summer_cool: '여름 쿨',
  winter_bright: '겨울 브라이트',
  winter_deep: '겨울 딥',
  winter_cool: '겨울 쿨',
  unknown: '몰라요',
};

export const PERSONAL_COLOR_OPTIONS = [
  { value: 'spring_light', label: '봄 라이트', mood: '밝고 화사한 색', emoji: '🌼' },
  { value: 'spring_bright', label: '봄 브라이트', mood: '쨍하고 생생한 색', emoji: '🍊' },
  { value: 'spring_warm', label: '봄 웜', mood: '부드럽고 생기있는 색', emoji: '🍑' },
  { value: 'autumn_muted', label: '가을 뮤트', mood: '차분하고 편안한 색', emoji: '🌾' },
  { value: 'autumn_deep', label: '가을 딥', mood: '깊고 어두운 색', emoji: '🍫' },
  { value: 'autumn_warm', label: '가을 웜', mood: '따뜻하고 성숙한 색', emoji: '🧡' },
  { value: 'summer_light', label: '여름 라이트', mood: '맑고 연한 색', emoji: '🫐' },
  { value: 'summer_muted', label: '여름 뮤트', mood: '은은하고 회색빛이 섞인 색', emoji: '☁️' },
  { value: 'summer_cool', label: '여름 쿨', mood: '시원하고 또렷한 색', emoji: '🩵' },
  { value: 'winter_bright', label: '겨울 브라이트', mood: '확 띄고 진한 색', emoji: '💄' },
  { value: 'winter_deep', label: '겨울 딥', mood: '아주 어둡고 묵직한 색', emoji: '🌌' },
  { value: 'winter_cool', label: '겨울 쿨', mood: '차갑고 선명한 색', emoji: '🧊' },
];

export const COLOR_ENTRY_OPTIONS = [
  { value: 'direct', title: '알아! 바로 선택할래', description: '12가지 퍼스널 컬러 중에서 바로 고를래', emoji: '💅' },
  { value: 'unknown', title: '모르겠어 ... 진단해줘', description: '몰라요일 때만 진단 설문으로 찾아볼게', emoji: '🔎' },
];

export const TONE_QUESTIONS = [
  {
    key: 'Q1',
    stepLabel: '1단계 / 2단계',
    title: '내 피부 바탕색은?',
    subtitle: '두 가지 질문으로 톤을 찾을게!',
    question: '손목 안쪽을 봤을 때, 혈관이 어떤 색으로 보여?',
    answers: [
      { value: 'A', title: '초록색이나 올리브색 💚', description: '웜 톤 가능성 ↑' },
      { value: 'B', title: '파란색이나 보라색 💙', description: '쿨 톤 가능성 ↑' },
    ],
  },
  {
    key: 'Q2',
    stepLabel: '1단계 / 2단계',
    title: '햇빛 아래의 내 피부는?',
    subtitle: '두 번째 질문으로 톤을 더 또렷하게 볼게!',
    question: '햇볕 아래에서 오래 놀고 나면 피부가 어떻게 돼?',
    answers: [
      { value: 'A', title: '갈색으로 타는 편 🤎', description: '웜 톤 가능성 ↑' },
      { value: 'B', title: '빨개졌다가 금방 돌아와 ❤️', description: '쿨 톤 가능성 ↑' },
    ],
  },
  {
    key: 'Q3',
    stepLabel: '1단계 / 2단계',
    title: '눈동자 바탕색은?',
    subtitle: '마지막 질문으로 웜/쿨을 정리할게!',
    question: '밝은 곳에서 봤을 때, 홍채 바탕색은 어느 쪽에 가까워?',
    answers: [
      { value: 'A', title: '노란빛 도는 밝은 갈색 🤎', description: '웜 톤 가능성 ↑' },
      { value: 'B', title: '짙은 고동색 / 회갈색 / 흑색 🖤', description: '쿨 톤 가능성 ↑' },
    ],
  },
];

export const WARM_OPTIONS = [
  { followup: 'A', value: 'spring_light', label: '봄 라이트', description: '밝고 화사한 색', emoji: '🌼' },
  { followup: 'B', value: 'spring_bright', label: '봄 브라이트', description: '쨍하고 생생한 색', emoji: '🍊' },
  { followup: 'B', value: 'spring_warm', label: '봄 웜', description: '파릇하고 깊은 색', emoji: '🍑' },
  { followup: 'C', value: 'autumn_muted', label: '가을 뮤트', description: '자연이고 포근한 색', emoji: '🌾' },
  { followup: 'D', value: 'autumn_deep', label: '가을 딥', description: '깊고 어두운 색', emoji: '🍫' },
  { followup: 'D', value: 'autumn_warm', label: '가을 웜', description: '따뜻하고 성숙한 색', emoji: '🧡' },
];

export const COOL_OPTIONS = [
  { followup: 'A', value: 'summer_light', label: '여름 라이트', description: '맑고 연한 색', emoji: '🩵' },
  { followup: 'B', value: 'summer_muted', label: '여름 뮤트', description: '은은하고 회청한 색', emoji: '☁️' },
  { followup: 'B', value: 'summer_cool', label: '여름 쿨', description: '시원하고 또렷한 색', emoji: '🌊' },
  { followup: 'C', value: 'winter_bright', label: '겨울 브라이트', description: '눈에 확 띄는 색', emoji: '💄' },
  { followup: 'D', value: 'winter_deep', label: '겨울 딥', description: '아주 어둡고 묵직한 색', emoji: '🌌' },
  { followup: 'D', value: 'winter_cool', label: '겨울 쿨', description: '차갑고 선명한 색', emoji: '🧊' },
];

export const STYLE_QUESTIONS = [
  {
    key: 'Qstyle_1',
    title: '새로운 사람들을 만나는 날, 거울 앞의 나는?',
    answers: [
      { value: 'A', title: '깔끔하고 단정하게!', description: '지적이면서 세련된 인상을 주고 싶어 ✨' },
      { value: 'B', title: '부드럽고 편안하게!', description: '금방 친해지고 싶은 사람처럼 보이고 싶어 ✌️' },
    ],
  },
  {
    key: 'Qstyle_2',
    title: '옷장에 입을 옷이 없어! 온라인 쇼핑 중 더 눈길이 가는 옷은?',
    answers: [
      { value: 'A', title: '기본템과 담백한 색감', description: '오래 입을 수 있는 실루엣이 좋아' },
      { value: 'B', title: '독특한 디테일과 포인트', description: '눈에 띄는 분위기의 아이템이 좋아' },
    ],
  },
  {
    key: 'Qstyle_4',
    title: '기다리고 기다리던 주말! 가장 기분 좋은 외출은?',
    answers: [
      { value: 'A', title: '예쁜 카페 / 핫플 코스', description: '사진 남기고 분위기 즐기기 📸' },
      { value: 'B', title: '산책 / 피크닉 / 활동 코스', description: '여기저기 돌아다니는 게 좋아' },
    ],
  },
  {
    key: 'Qstyle_5',
    title: '오랜만의 문화생활! 내가 더 끌리는 영화 포스터는?',
    answers: [
      { value: 'A', title: '차갑고 도시적인 장면', description: '절제된 톤, 시크한 주인공 🌃' },
      { value: 'B', title: '빈티지한 햇살과 로맨스 무드', description: '감성적인 장면, 몽글한 무드 ❤️' },
    ],
  },
  {
    key: 'Qstyle_6',
    title: '옷에서 좋아하는 포인트는?',
    answers: [
      { value: 'A', title: '심플하고 깔끔한 기본템', description: '로고나 패턴 없는 돌려 입기 좋은 아이템 🤍' },
      { value: 'B', title: '톡톡 튀는 포인트템', description: '흔하지 않은 디자인과 컬러 💖' },
    ],
  },
  {
    key: 'Qstyle_7',
    title: '내가 더 편하게 느끼는 코디 방식은?',
    answers: [
      { value: 'A', title: '힘 뺀 꾸안꾸', description: '자연스럽지만 센스 있는 스타일' },
      { value: 'B', title: '무드가 분명한 분위기형', description: '분위기 자체가 예쁘게 완성되는 스타일' },
    ],
  },
  {
    key: 'Qstyle_8',
    title: '새 옷을 보고 남들이 해줬으면 하는 말은?',
    answers: [
      { value: 'A', title: '자기 스타일 확실하다!', description: '멋있고 개성 있어 보여' },
      { value: 'B', title: '분위기 있다, 센스 있다!', description: '예쁘고 무드 있어 보여' },
    ],
  },
  {
    key: 'Qstyle_9',
    title: '오늘 중요한 약속이 있다! 옷을 고를 때 가장 먼저 드는 생각은?',
    answers: [
      { value: 'A', title: '일정에 맞게 단정하고 무난하게', description: '출근, 학교, 평소 외출처럼 자연스럽게' },
      { value: 'B', title: '예쁘고 호감 가게 입고 싶어', description: '데이트, 친구 약속, 사교 모임처럼' },
      { value: 'C', title: '격식 있게 갖춰 입어야 해', description: '행사, 결혼식, 중요한 모임처럼' },
      { value: 'D', title: '편하고 활동성 있게 입자', description: '레저, 스포츠, 여행처럼' },
    ],
  },
];

export const FIT_QUESTION = {
  key: 'Qstyle_3',
  title: '밥 먹고 배가 살짝 부른 상태! 지금 내 옷의 핏은?',
  answers: [
    { value: 'A', title: '정사이즈 / 핏이 중요해', description: '체형에 딱 맞는 타이트-노멀 핏이 좋아 📏' },
    { value: 'B', title: '넉넉한 사이즈가 편해', description: '루즈-오버핏으로 여유 있게 입고 싶어 👕' },
  ],
};

export const SURVEY_TOTAL_STEPS = STYLE_QUESTIONS.length + 1;

export const PERSONAS = {
  sophisticated: {
    code: 'sophisticated',
    label: '소피스티케이티드',
    emoji: '💻',
    headline: '갓생 사는 도심 속 차도녀/차도남',
    tagline: '8시 55분, 아아 한 잔과 함께 업무 모드 ON!',
    description: '아침 이슬 머금은 셔츠처럼 언제나 흐트러짐 없는 당신! 복잡한 도심 속에서도 나만의 칼각과 리듬을 지키는 프로페셔널한 타입이에요. 겉은 조금 시크해 보여도 계획한 일은 끝까지 해내고야 마는 반전 매력의 소유자랍니다.',
    items: ['잘 다려진 셔츠', '핏이 딱 떨어지는 슬랙스', '툭 걸쳐도 멋진 블레이저'],
    point: '단정하고 정돈된 느낌이 당신의 지적인 분위기를 200% 살려줄 거예요! ✨',
    styleTip: '블랙, 다크 블루처럼 조금 묵직한 컬러를 중심으로 갓생 오피스룩을 완성해봐. 블레이저 위에 무심하게 걸친 아우터면 더 세련돼 보여!',
  },
  feminine: {
    code: 'feminine',
    label: '페미닌',
    emoji: '🌸',
    headline: '호수 위의 백조, 우아함 한 스푼 여신',
    tagline: '은은하게 퍼지는 샴푸 향기처럼, 보는 사람 마음까지 몽글몽글하게 만드는 분위기 장인',
    description: '화사하게 피어난 꽃처럼 언제나 부드럽고 우아한 선을 사랑하는 당신! 차분한 카리스마로 주변을 밝히는 존재감을 가졌네요. 겉은 연약해 보여도 내면은 누구보다 단단하고 아름다운 매력의 소유자랍니다.',
    items: ['라인을 살려주는 원피스', '하늘하늘한 블라우스', '페미닌한 무드의 스커트'],
    point: '부드럽고 여성스러운 디테일이 당신의 우아한 이미지를 더욱 빛나게 해줄 거예요! ✨',
    styleTip: '부드러운 라인과 섬세한 디테일이 살아 있는 아이템을 고르면 분위기가 더 살아나.',
  },
  hipster_punk: {
    code: 'hipster_punk',
    label: '힙스터/펑크',
    emoji: '🎸',
    headline: '톡톡 튀는 인간 팝핑캔디',
    tagline: '남들 다 하는 건 노잼! 톡 쏘는 탄산처럼 강렬한 존재감의 패션 모험가',
    description: '평범한 건 거부한다! 독특하고 화려한 스타일로 자신을 표현할 줄 아는 용감한 타입이에요. 트렌드를 따라가기보다 나만의 트렌드를 직접 만들어가는 쿨한 감각을 가졌네요.',
    items: ['화려한 패턴의 상의', '독특한 워싱의 데님', '시선 강탈 포인트 액세서리'],
    point: '화려하고 독특한 개성이 당신의 힙한 감성을 200% 완성해 줄 거예요! 😎',
    styleTip: '강한 포인트 하나만 넣어도 룩의 존재감이 확 살아나는 타입이야.',
  },
  casual: {
    code: 'casual',
    label: '캐주얼',
    emoji: '🎒',
    headline: '어디서나 찰떡! 호불호 제로 카멜레온',
    tagline: '햇살 좋은 등굣길 단짝 친구 같은 편안함, 알면 알수록 자꾸 보고 싶은 마성의 꾸안꾸',
    description: '무심한 듯 툭 걸친 티셔츠 한 장으로도 완벽한 밸런스를 찾아내는 자연스러움의 대명사! 어떤 모임에 가도 편안하게 스며드는 친근한 매력을 가졌어요.',
    items: ['편안한 맨투맨', '활동성 좋은 데님 팬츠', '가벼운 캔버스화'],
    point: '실용적이고 깔끔한 느낌이 당신의 맑고 깨끗한 분위기를 200% 살려줄 거예요! ✨',
    styleTip: '편안함을 기본으로, 핏과 컬러만 정리해도 깔끔한 꾸안꾸가 완성돼.',
  },
  modern_minimal: {
    code: 'modern_minimal',
    label: '모던/미니멀',
    emoji: '🧊',
    headline: '군더더기 제로, 시크한 얼음물 한 잔',
    tagline: '비움의 미학을 아는 차분한 아우라, 단순함 속에 숨겨진 묵직한 카리스마',
    description: '복잡한 건 딱 질색! 깔끔한 선과 무채색의 조화로운 무드를 즐기는 냉철한 감각가예요. 화려하게 꾸미지 않아도 정갈한 분위기가 사람들의 시선을 사로잡죠.',
    items: ['무채색 코트나 재킷', '로고 없는 니트', '딱 떨어지는 슬랙스'],
    point: '깔끔하고 무난한 핏이 오히려 당신의 감각적인 카리스마를 더욱 돋보이게 해줄 거예요! 🧊',
    styleTip: '장식을 줄이고 실루엣을 살리면 미니멀 무드가 훨씬 선명해져.',
  },
  romantic: {
    code: 'romantic',
    label: '로맨틱',
    emoji: '🎀',
    headline: '인간 벚꽃 솜사탕, 사랑스러움의 결정체',
    tagline: '바라만 봐도 기분이 좋아지는 따뜻한 봄 햇살, 주변을 핑크빛으로 물들이는 러블리 요정',
    description: '포근하고 다정한 마음씨만큼이나 사랑스러운 스타일을 추구하는 로맨티스트! 부드러운 색감과 발랄한 디테일로 주변 사람들에게 기분 좋은 에너지를 전해줘요.',
    items: ['파스텔 톤 가디건', '리본 디테일 블라우스', '부드러운 니트 아이템'],
    point: '부드럽고 발랄한 무드가 당신의 사랑스러운 매력을 200% 폭발시켜줄 거예요! 💖',
    styleTip: '파스텔과 디테일 포인트를 살리면 로맨틱한 분위기가 자연스럽게 살아나.',
  },
  mannish: {
    code: 'mannish',
    label: '매니시',
    emoji: '🕴️',
    headline: '무심한 듯 툭, 시크한 선배미 뿜뿜',
    tagline: '묵직한 베이스 기타 소리처럼 멋진 울림, 중성적인 매력에 자꾸만 눈길이 가는 차가운 도시인',
    description: '도시적이고 멋진 이미지를 선호하며, 자신만의 뚜렷한 주관을 스타일로 표현할 줄 알아요. 남성적인 아이템도 쿨하게 소화하는 단단한 내면의 소유자예요.',
    items: ['오버핏 자켓', '와이드 슬랙스', '클래식한 옥스포드화'],
    point: '도시적이면서도 멋있는 분위기가 당신의 쿨한 멋을 200% 완성해 줄 거예요! 😎',
    styleTip: '힘 있는 실루엣과 차분한 톤이 가장 잘 어울리는 타입이야.',
  },
  street: {
    code: 'street',
    label: '스트리트',
    emoji: '🛹',
    headline: '뒷골목 런웨이, 자유로운 영혼의 지배자',
    tagline: '스케이트보드와 비니가 잘 어울리는 힙한 댕댕이, 정해진 틀을 깨부수는 거리의 주인공',
    description: '어디로 튈지 모르는 자유로운 에너지와 트렌디한 감각이 공존하는 당신! 나만의 개성을 담은 힙한 스타일링을 즐기는 타입이에요.',
    items: ['편안한 후드티', '넉넉한 카고 팬츠', '트렌디한 조거 팬츠'],
    point: '활동적이고 트렌디한 무드가 당신의 자유로운 영혼을 200% 보여줄 거예요! 🛹',
    styleTip: '실루엣에 볼륨을 주고, 포인트 하나만 넣어도 스트리트 무드가 살아나.',
  },
  sporty: {
    code: 'sporty',
    label: '스포티',
    emoji: '🏃‍♀️',
    headline: '에너지 1000%, 지치지 않는 인간 비타민',
    tagline: '트랙 위를 달리는 생기발랄함 그 자체! 존재만으로도 주변을 환하게 밝히는 에너자이저',
    description: '건강한 에너지와 활동적인 스타일이 당신의 가장 큰 매력 포인트! 입는 사람도 보는 사람도 편안하게 만드는 생기 넘치는 스타일을 사랑하는군요.',
    items: ['아노락 자켓', '레깅스나 트레이닝 셋업', '야구 모자'],
    point: '활동적이고 편안한 핏이 당신의 건강한 이미지를 200% 완성해 줄 거예요! ⚡',
    styleTip: '활동성을 살리는 소재와 핏을 고르면 스포티 무드가 가장 예쁘게 살아나.',
  },
  retro: {
    code: 'retro',
    label: '레트로/빈티지',
    emoji: '📻',
    headline: '낭만 가득한 시간여행자',
    tagline: '할머니 옷장 속 보물을 찾아낸 듯한 설렘, 아날로그 필름 카메라 속에 담긴 따뜻한 기록',
    description: '남들은 모르는 독특한 색감과 과거의 낭만을 찾아 여행하는 아날로그 감성가! 유행보다 나만의 추억과 이야기를 담은 옷들을 소중히 여기는 섬세한 취향을 가졌네요.',
    items: ['체크무늬 셔츠', '코듀로이 팬츠', '빛바랜 그래픽 티셔츠'],
    point: '독특하고 트렌디한 빈티지 감성이 당신의 깊은 매력을 200% 담아내 줄 거예요! 📻',
    styleTip: '텍스처가 느껴지는 소재와 빈티지한 톤을 섞으면 깊은 매력이 살아나.',
  },
};

export const CATEGORY_OPTIONS = ['상의', '아우터', '팬츠', '니트/카디건', '원피스', '스커트', '트레이닝'];

export const MUSINSA_CATEGORY_MAP = {
  상의: '상의',
  아우터: '아우터',
  팬츠: '팬츠',
  '니트/카디건': '니트/카디건',
  원피스: '미디원피스',
  스커트: '미디스커트',
  트레이닝: '트레이닝',
};

export const COLOR_FILTER_OPTIONS = [
  { value: '', label: '자동 추천' },
  { value: '화이트', label: '화이트' },
  { value: '아이보리', label: '아이보리' },
  { value: '핑크', label: '핑크' },
  { value: '블루', label: '블루' },
  { value: '네이비', label: '네이비' },
  { value: '베이지', label: '베이지' },
  { value: '브라운', label: '브라운' },
  { value: '그레이', label: '그레이' },
  { value: '블랙', label: '블랙' },
];

export function resolvePersonaImagePath(code, gender) {
  const suffix = String(gender || 'W').toUpperCase() === 'M' ? 'm' : 'w';
  return `./assets/images/${code}_${suffix}.png`;
}

export function resolveGenderImagePath(gender) {
  return String(gender || 'W').toUpperCase() === 'M'
    ? './assets/images/male_select.png'
    : './assets/images/female_select.png';
}

export function personalColorLabel(code) {
  return PERSONAL_COLOR_LABELS[code] || code || '-';
}
