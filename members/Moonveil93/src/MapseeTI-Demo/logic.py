import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field

class FashionPersona(BaseModel):
    persona_name: str = Field(description="감성적인 페르소나 타이틀 (예: '도심 속의 미니멀리스트')")
    persona_description: str = Field(description="성별과 취향을 조합한 2~3문장의 깊이 있는 설명")
    styling_tip: str = Field(description="구체적인 배색과 아이템을 포함한 3줄 상세 팁")
    point_color: str = Field(description="무신사와 지그재그 기반의 포인트 컬러 제안 (2줄)")

def analyze_fashion_style(api_key, gender, personal_color, quiz_answers, musinsa_colors, zigzag_colors):
    """
    OpenAI GPT-4o-mini를 사용하여 사용자의 패션 스타일을 분석합니다.
    """
    actual_api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not actual_api_key:
        return {"error": "OpenAI API Key가 설정되지 않았습니다."}

    try:
        llm = ChatOpenAI(model="gpt-4o-mini", api_key=actual_api_key, temperature=0.7)
        structured_llm = llm.with_structured_output(FashionPersona)

        template = """
        당신은 독보적인 감각을 지닌 프리미엄 패션 에디터이자 스타일 디렉터입니다. 
        사용자의 데이터를 바탕으로 한 편의 시적인 '맵시 페르소나' 서사와 쇼핑 가이드를 작성하세요.

        [입력 데이터]
        - 성별: {gender}
        - 퍼스널 컬러: {personal_color}
        - 핵심 취향 (Top 3): {top_styles}
        - 선호하는 실루엣: {preferred_fit}
        - **무신사 구매 가능 컬러**: {musinsa_colors}
        - **지그재그 구매 가능 컬러**: {zigzag_colors}

        [페르소나 생성 가이드라인]
        1. **퍼스널 컬러의 영혼**: {personal_color}의 특징을 깊이 있게 녹여내세요.
        2. **스타일 융합**: {top_styles}와 {preferred_fit}을 하나의 라이프스타일로 엮어 매력적인 페르소나 타이틀을 지으세요.
        3. **전략적 포인트 컬러 (중요 - 2줄 출력)**: 
           - 'point_color' 필드에 반드시 다음 형식으로 **두 줄**을 작성하세요.
           - 첫 번째 줄: **[무신사 구매 가능 컬러]** 중 하나를 골라 감성적 수식어를 붙여 작성하세요. (예: 안갯속 가을 숲을 닮은 깊은 **카멜**)
           - 두 번째 줄: **[지그재그 구매 가능 컬러]** 중 하나를 골라 감성적 수식어를 붙여 작성하세요. (예: 노을빛을 머금은 부드러운 **베이지**)
           - **주의**: '무신사', '지그재그'와 같은 커머스 사이트 명칭은 문장에 절대 포함하지 마세요. 오직 감성적인 색상 묘사만 작성합니다.
        4. **전문적 조언**: 스타일링 팁은 구체적인 소재와 아이템을 언급하여 에디터의 전문성을 보여주세요.

        [언어] 한국어로 친절하고 우아하게 답변하세요.
        """

        prompt = PromptTemplate(
            template=template,
            input_variables=["gender", "personal_color", "top_styles", "preferred_fit", "musinsa_colors", "zigzag_colors"]
        )

        chain = prompt | structured_llm
        
        result = chain.invoke({
            "gender": gender,
            "personal_color": personal_color,
            "top_styles": ", ".join(quiz_answers.get("top_styles", [])),
            "preferred_fit": quiz_answers.get("preferred_fit", "노멀 핏"),
            "musinsa_colors": ", ".join(musinsa_colors),
            "zigzag_colors": ", ".join(zigzag_colors)
        })
        
        return result.model_dump()
        
    except Exception as e:
        return {"error": f"분석 중 오류 발생: {str(e)}"}
