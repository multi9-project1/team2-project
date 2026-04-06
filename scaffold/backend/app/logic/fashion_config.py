from __future__ import annotations

from typing import Dict, List

PERSONAL_COLOR_LABELS: Dict[str, str] = {
    "spring_light": "봄 라이트",
    "spring_bright": "봄 브라이트",
    "spring_warm": "봄 웜",
    "summer_light": "여름 라이트",
    "summer_muted": "여름 뮤트",
    "summer_cool": "여름 쿨",
    "autumn_muted": "가을 뮤트",
    "autumn_deep": "가을 딥",
    "autumn_warm": "가을 웜",
    "winter_bright": "겨울 브라이트",
    "winter_deep": "겨울 딥",
    "winter_cool": "겨울 쿨",
    "unknown": "모르겠음",
}

PERSONAL_COLOR_ALIASES: Dict[str, str] = {
    "spring_light": "spring_light",
    "spring_bright": "spring_bright",
    "spring_warm": "spring_warm",
    "summer_light": "summer_light",
    "summer_muted": "summer_muted",
    "summer_cool": "summer_cool",
    "autumn_muted": "autumn_muted",
    "autumn_deep": "autumn_deep",
    "autumn_warm": "autumn_warm",
    "winter_bright": "winter_bright",
    "winter_deep": "winter_deep",
    "winter_cool": "winter_cool",
    "봄 라이트": "spring_light",
    "봄 브라이트": "spring_bright",
    "봄 웜": "spring_warm",
    "여름 라이트": "summer_light",
    "여름 뮤트": "summer_muted",
    "여름 쿨": "summer_cool",
    "가을 뮤트": "autumn_muted",
    "가을 딥": "autumn_deep",
    "가을 웜": "autumn_warm",
    "겨울 브라이트": "winter_bright",
    "겨울 딥": "winter_deep",
    "겨울 쿨": "winter_cool",
    "모르겠음": "unknown",
    "unknown": "unknown",
}

PERSONAL_COLOR_REPRESENTATIVE_COLORS: Dict[str, List[str]] = {
    "spring_light": ["페일 옐로우", "라이트 코랄"],
    "spring_bright": ["비비드 오렌지", "애플 그린"],
    "spring_warm": ["골든 옐로우", "웜 핑크"],
    "summer_light": ["파우더 블루", "라벤더"],
    "summer_muted": ["스모키 블루", "로즈 그레이"],
    "summer_cool": ["스카이 블루", "실버 화이트"],
    "autumn_muted": ["소프트 카키", "베이지"],
    "autumn_deep": ["테라코타", "다크 브라운"],
    "autumn_warm": ["머스터드", "펌킨 오렌지"],
    "winter_bright": ["로열 블루", "핫 핑크"],
    "winter_deep": ["버건디", "포레스트 그린"],
    "winter_cool": ["퓨어 화이트", "네이비"],
    "unknown": [],
}

PERSONAL_COLOR_DATASET_TARGETS: Dict[str, tuple[int, int, int]] = {
    "spring_light": (2, 2, 2),
    "spring_bright": (2, 2, 2),
    "spring_warm": (2, 2, 2),
    "summer_light": (2, 1, 2),
    "summer_muted": (2, 1, 2),
    "summer_cool": (2, 1, 2),
    "autumn_muted": (1, 2, 1),
    "autumn_deep": (1, 2, 1),
    "autumn_warm": (1, 2, 1),
    "winter_bright": (2, 1, 1),
    "winter_deep": (1, 1, 1),
    "winter_cool": (2, 1, 1),
}

STYLE_CODE_ORDER: List[str] = [
    "sophisticated",
    "modern_minimal",
    "feminine",
    "mannish",
    "casual",
    "romantic",
    "street",
    "sporty",
    "hipster_punk",
    "retro",
]

STYLE_LABELS: Dict[str, str] = {
    "sophisticated": "소피스티케이티드",
    "modern_minimal": "모던/미니멀",
    "feminine": "페미닌",
    "mannish": "매니시",
    "casual": "캐주얼",
    "romantic": "로맨틱",
    "street": "스트리트",
    "sporty": "스포티",
    "hipster_punk": "힙스터/펑크",
    "retro": "레트로",
}

STYLE_KEYWORD_MAP: Dict[str, List[str]] = {
    "sophisticated": ["세련된", "소피스티케이티드"],
    "modern_minimal": ["미니멀", "모던"],
    "feminine": ["페미닌", "여성스러운"],
    "mannish": ["매니시", "젠더리스"],
    "casual": ["캐주얼", "데일리"],
    "romantic": ["로맨틱", "러블리"],
    "street": ["스트리트", "힙"],
    "sporty": ["스포티", "애슬레저"],
    "hipster_punk": ["펑크", "힙스터"],
    "retro": ["레트로", "빈티지"],
}

PERSONAL_COLOR_KEYWORD_MAP: Dict[str, List[str]] = {
    "spring_light": ["라이트 핑크", "페일 옐로우", "코랄"],
    "spring_bright": ["비비드 오렌지", "애플 그린", "브라이트 코랄"],
    "spring_warm": ["골든 옐로우", "웜 핑크", "피치"],
    "summer_light": ["파우더 블루", "라벤더", "라이트 그레이"],
    "summer_muted": ["스모키 블루", "로즈 그레이", "뮤트 핑크"],
    "summer_cool": ["스카이 블루", "실버 화이트", "쿨 핑크"],
    "autumn_muted": ["소프트 카키", "베이지", "웜 그레이"],
    "autumn_deep": ["테라코타", "다크 브라운", "카멜"],
    "autumn_warm": ["머스터드", "펌킨 오렌지", "올리브"],
    "winter_bright": ["로열 블루", "핫 핑크", "비비드 화이트"],
    "winter_deep": ["버건디", "포레스트 그린", "차콜"],
    "winter_cool": ["퓨어 화이트", "네이비", "쿨 블루"],
    "unknown": [],
}

DATASET_STYLE_LABELS: Dict[str, str] = {
    "athleisure": "애슬레저룩",
    "bodyconscious": "바디컨셔스룩",
    "bold": "볼드룩",
    "cityglam": "시티글램룩",
    "classic": "클래식룩",
    "disco": "디스코룩",
    "ecology": "에콜로지룩",
    "feminine": "페미닌룩",
    "genderless": "젠더리스룩",
    "grunge": "그런지룩",
    "hiphop": "힙합룩",
    "hippie": "히피룩",
    "ivy": "아이비룩",
    "kitsch": "키치룩",
    "lingerie": "란제리룩",
    "lounge": "라운지룩",
    "metrosexual": "메트로섹슈얼룩",
    "military": "밀리터리룩",
    "minimal": "미니멀룩",
    "mods": "모즈룩",
    "normcore": "놈코어룩",
    "oriental": "오리엔탈룩",
    "popart": "팝아트룩",
    "powersuit": "파워수트룩",
    "punk": "펑크룩",
    "space": "스페이스룩",
    "sportivecasual": "스포티브 캐주얼룩",
}

DATASET_STYLE_GROUP_LABELS: Dict[str, str] = {
    "cityglam": "소피스티케이티드",
    "powersuit": "소피스티케이티드",
    "classic": "소피스티케이티드",
    "feminine": "페미닌",
    "bodyconscious": "페미닌",
    "lingerie": "로맨틱",
    "oriental": "로맨틱",
    "minimal": "모던/미니멀",
    "normcore": "모던/미니멀",
    "ivy": "캐주얼",
    "lounge": "캐주얼",
    "ecology": "캐주얼",
    "genderless": "매니시",
    "metrosexual": "매니시",
    "military": "매니시",
    "hiphop": "스트릿",
    "bold": "스트릿",
    "athleisure": "스포티",
    "sportivecasual": "스포티",
    "punk": "힙스터/펑크",
    "grunge": "힙스터/펑크",
    "kitsch": "힙스터/펑크",
    "mods": "레트로/빈티지",
    "popart": "레트로/빈티지",
    "space": "레트로/빈티지",
    "disco": "레트로/빈티지",
    "hippie": "레트로/빈티지",
}

STYLE_GROUP_TO_STYLE_CODE: Dict[str, str] = {
    "소피스티케이티드": "sophisticated",
    "페미닌": "feminine",
    "로맨틱": "romantic",
    "모던/미니멀": "modern_minimal",
    "캐주얼": "casual",
    "매니시": "mannish",
    "스트릿": "street",
    "스포티": "sporty",
    "힙스터/펑크": "hipster_punk",
    "레트로/빈티지": "retro",
}

STYLE_RANKING_WEIGHT_MAP: Dict[str, Dict[str, float]] = {
    "default": {"style": 0.75, "fit": 0.20, "color": 0.05, "group_bonus": 0.0},
    "retro": {"style": 0.82, "fit": 0.08, "color": 0.05, "group_bonus": 0.05},
    "hipster_punk": {"style": 0.82, "fit": 0.08, "color": 0.05, "group_bonus": 0.05},
    "street": {"style": 0.80, "fit": 0.10, "color": 0.05, "group_bonus": 0.05},
    "sporty": {"style": 0.70, "fit": 0.20, "color": 0.05, "group_bonus": 0.05},
}

STYLE_QUESTION_OPTION_STYLE_MAP: Dict[str, Dict[str, List[str]]] = {
    "Qstyle_1": {
        "A": ["sophisticated", "modern_minimal", "mannish"],
        "B": ["casual", "romantic", "feminine"],
    },
    "Qstyle_2": {
        "A": ["modern_minimal", "casual", "sophisticated"],
        "B": ["street", "hipster_punk", "retro"],
    },
    "Qstyle_4": {
        "A": ["feminine", "romantic", "retro"],
        "B": ["sporty", "street", "casual"],
    },
    "Qstyle_5": {
        "A": ["mannish", "modern_minimal", "street"],
        "B": ["romantic", "retro", "feminine"],
    },
    "Qstyle_6": {
        "A": ["sophisticated", "mannish", "modern_minimal"],
        "B": ["hipster_punk", "street", "sporty"],
    },
    "Qstyle_7": {
        "A": ["casual", "sporty", "hipster_punk"],
        "B": ["feminine", "romantic", "sophisticated"],
    },
    "Qstyle_8": {
        "A": ["mannish", "hipster_punk", "street"],
        "B": ["modern_minimal", "retro", "sporty"],
    },
}

STYLE_DATASET_FEATURE_MAP: Dict[str, List[str]] = {
    "sophisticated": ["Q4202", "Q4204"],
    "feminine": ["Q4214", "Q4216"],
    "hipster_punk": ["Q4209", "Q4206", "Q4207"],
    "casual": ["Q4210", "Q4212"],
    "modern_minimal": ["Q4205", "Q4208"],
    "romantic": ["Q4213", "Q4216"],
    "mannish": ["Q4215", "Q4202"],
    "street": ["Q4207", "Q4203"],
    "sporty": ["Q4211", "Q4212"],
    "retro": ["Q4207"],
}

TPO_OPTION_TO_DATASET_Q3_VALUES: Dict[str, List[int]] = {
    "A": [1, 5],
    "B": [2, 4],
    "C": [3],
    "D": [6, 7],
}

TPO_OPTION_TO_DEEPLINK_KEYWORD: Dict[str, str] = {
    "A": "출근룩",
    "B": "데이트룩",
    "C": "하객룩",
    "D": "레저룩",
}

FIT_PREFERENCE_TO_Q411_SCORE = {
    "T": {2: 1.0, 3: 0.8, 1: 0.2},
    "L": {1: 1.0, 2: 0.4, 3: 0.0},
}

WARM_PERSONAL_COLOR_BRANCH_MAP = {
    "A": "spring_light",
    "B": "spring_bright",
    "C": "autumn_muted",
    "D": "autumn_deep",
}

COOL_PERSONAL_COLOR_BRANCH_MAP = {
    "A": "summer_light",
    "B": "summer_muted",
    "C": "winter_bright",
    "D": "winter_deep",
}

MOCK_DATASET_ITEMS = [
    {
        "item_id": "mock_001",
        "image_path": "mock://lookbook/winter_minimal_01.jpg",
        "gender": "W",
        "era": "2020",
        "style": "modern",
        "Q411": 1,
        "Q412": 1,
        "Q413": 1,
        "Q414": 1,
        "Q4202": 1,
        "Q4205": 1,
        "Q4208": 1,
        "Q4215": 1,
    },
    {
        "item_id": "mock_002",
        "image_path": "mock://lookbook/spring_feminine_01.jpg",
        "gender": "W",
        "era": "2021",
        "style": "romantic",
        "Q411": 2,
        "Q412": 2,
        "Q413": 2,
        "Q414": 2,
        "Q4214": 1,
        "Q4216": 1,
        "Q4213": 1,
        "Q4204": 1,
    },
    {
        "item_id": "mock_003",
        "image_path": "mock://lookbook/casual_street_01.jpg",
        "gender": "U",
        "era": "2010",
        "style": "street",
        "Q411": 1,
        "Q412": 2,
        "Q413": 1,
        "Q414": 2,
        "Q4207": 1,
        "Q4203": 1,
        "Q4210": 1,
        "Q4212": 1,
    },
    {
        "item_id": "mock_004",
        "image_path": "mock://lookbook/autumn_sophisticated_01.jpg",
        "gender": "M",
        "era": "2018",
        "style": "classic",
        "Q411": 2,
        "Q412": 1,
        "Q413": 2,
        "Q414": 1,
        "Q4202": 1,
        "Q4204": 1,
        "Q4215": 1,
    },
    {
        "item_id": "mock_005",
        "image_path": "mock://lookbook/sporty_cool_01.jpg",
        "gender": "U",
        "era": "2022",
        "style": "sporty",
        "Q411": 1,
        "Q412": 2,
        "Q413": 1,
        "Q414": 1,
        "Q4211": 1,
        "Q4212": 1,
        "Q4207": 1,
    },
]