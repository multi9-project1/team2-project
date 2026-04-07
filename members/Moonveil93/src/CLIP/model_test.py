import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
import torch
import pandas as pd
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
from tqdm import tqdm

# ==========================================
# 1. 환경 설정 및 모델 로드
# ==========================================
MODEL_PATH = "./fine_tuned_clip_fashion" 
# 테스트할 사진들이 들어있는 폴더 경로를 지정하세요
TEST_IMAGE_DIR = r"C:/Users/kmg14/Desktop/프로젝트 관련/Map-si TI/fine_tuned_clip_fashion/test_image" 
OUTPUT_CSV = "style_analysis_results.csv"

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

print(f"⏳ 학습된 모델 로드 중: {MODEL_PATH}")
model = CLIPModel.from_pretrained(MODEL_PATH).to(device)
processor = CLIPProcessor.from_pretrained(MODEL_PATH)
model.eval()

# 비교할 10가지 스타일 라벨 (학습 시 사용한 키워드)
candidate_labels = [
    "casual fashion", "streetwear fashion", "office wear fashion", 
    "feminine fashion", "mannish fashion", "sporty fashion", 
    "modern minimal fashion", "romantic fashion", "hipster fashion", "retro fashion"
]

# ==========================================
# 2. 폴더 내 이미지 파일 목록 가져오기
# ==========================================
valid_extensions = ('.jpg', '.jpeg', '.png', '.webp')
image_files = [f for f in os.listdir(TEST_IMAGE_DIR) if f.lower().endswith(valid_extensions)]

print(f"🚀 총 {len(image_files)}장의 사진 분석을 시작합니다.")

results = []

# ==========================================
# 3. 루프 돌며 분석 진행
# ==========================================
with torch.no_grad():
    for filename in tqdm(image_files, desc="스타일 분석 중"):
        img_path = os.path.join(TEST_IMAGE_DIR, filename)
        
        try:
            # 이미지 로드 및 전처리
            image = Image.open(img_path).convert("RGB")
            inputs = processor(
                text=candidate_labels, 
                images=image, 
                return_tensors="pt", 
                padding=True
            ).to(device)

            # 모델 추론
            outputs = model(**inputs)
            
            # 유사도 점수 계산 (확률값 0~1 사이로 변환)
            logits_per_image = outputs.logits_per_image
            probs = logits_per_image.softmax(dim=1).cpu().numpy()[0]

            # 결과 데이터 정리
            entry = {"file_name": filename}
            for label, prob in zip(candidate_labels, probs):
                entry[label] = round(float(prob), 4)  # 소수점 4자리까지 저장
            
            # 가장 점수가 높은 스타일 기록
            entry["top_style"] = candidate_labels[probs.argmax()]
            entry["confidence"] = round(float(probs.max()), 4)
            
            results.append(entry)

        except Exception as e:
            print(f"\n⚠️ {filename} 처리 중 오류 발생: {e}")

# ==========================================
# 4. CSV 파일로 저장
# ==========================================
if results:
    df = pd.DataFrame(results)
    # 컬럼 순서 조정 (파일명, 최고스타일, 확신도, 나머지 스타일들...)
    cols = ["file_name", "top_style", "confidence"] + candidate_labels
    df = df[cols]
    
    df.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')
    print(f"\n✅ 분석 완료! 결과가 '{OUTPUT_CSV}'에 저장되었습니다.")
else:
    print("\n❌ 분석된 결과가 없습니다.")