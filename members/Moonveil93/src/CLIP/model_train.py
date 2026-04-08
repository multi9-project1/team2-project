import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True' 

import torch
import pandas as pd
from PIL import Image

import os
import torch
import pandas as pd
from PIL import Image
from torch.utils.data import Dataset, DataLoader
from transformers import CLIPProcessor, CLIPModel
from torch.optim import AdamW
from torch.cuda.amp import autocast, GradScaler
from tqdm import tqdm

# ==========================================
# 1. 하이퍼파라미터 및 경로 설정
# ==========================================
CSV_FILE = "H:/data/010.연도별 패션 선호도 파악 및 추천 데이터/01-1.정식개방데이터/huggingface/Training/clip_training_data.csv"
IMAGE_DIR = r"H:/data/010.연도별 패션 선호도 파악 및 추천 데이터/01-1.정식개방데이터/huggingface/Training/원본데이터"
MODEL_NAME = "openai/clip-vit-base-patch32"
BATCH_SIZE = 8                                
EPOCHS = 3
LEARNING_RATE = 5e-6
SAVE_DIR = "./fine_tuned_clip_fashion"

# ==========================================
# 2. 커스텀 데이터셋 클래스 (이전과 동일)
# ==========================================
class FashionCLIPDataset(Dataset):
    def __init__(self, csv_file, img_dir, processor):
        self.data_frame = pd.read_csv(csv_file)
        self.img_dir = img_dir
        self.processor = processor

    def __len__(self):
        return len(self.data_frame)

    def __getitem__(self, idx):
        img_name = self.data_frame.iloc[idx]['image_path']
        caption = self.data_frame.iloc[idx]['caption']
        img_path = os.path.join(self.img_dir, img_name)

        try:
            image = Image.open(img_path).convert("RGB")
        except Exception:
            image = Image.new('RGB', (224, 224), (0, 0, 0))

        inputs = self.processor(
            text=caption, 
            images=image, 
            return_tensors="pt", 
            padding="max_length", 
            truncation=True, 
            max_length=77
        )
        
        return {
            "pixel_values": inputs["pixel_values"].squeeze(0),
            "input_ids": inputs["input_ids"].squeeze(0),
            "attention_mask": inputs["attention_mask"].squeeze(0)
        }

# ==========================================
# 3. 학습 메인 로직 (AMP 적용)
# ==========================================
def train_model():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"🖥️ 현재 장치: {device} (RTX 2080 출동!)")

    model = CLIPModel.from_pretrained(MODEL_NAME).to(device)
    processor = CLIPProcessor.from_pretrained(MODEL_NAME)

    dataset = FashionCLIPDataset(CSV_FILE, IMAGE_DIR, processor)
    
    # 💡 num_workers=4 를 추가하여 CPU(9700k)의 남는 힘을 데이터 로딩에 활용!
    dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=4)

    optimizer = AdamW(model.parameters(), lr=LEARNING_RATE, weight_decay=0.01)
    
    scaler = GradScaler() # 💡 메모리 절약 및 속도 향상을 위한 Scaler 객체 생성

    print(f"🚀 총 {len(dataset)}개의 데이터 학습 시작! (Epochs: {EPOCHS}, Batch: {BATCH_SIZE})")
    model.train()

    for epoch in range(EPOCHS):
        total_loss = 0
        progress_bar = tqdm(dataloader, desc=f"Epoch {epoch+1}/{EPOCHS}")

        for batch in progress_bar:
            pixel_values = batch["pixel_values"].to(device)
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)

            optimizer.zero_grad()

            # 💡 autocast()를 사용하여 연산 효율을 극대화 (VRAM 절약)
            with autocast():
                outputs = model(
                    input_ids=input_ids,
                    pixel_values=pixel_values,
                    attention_mask=attention_mask,
                    return_loss=True
                )
                loss = outputs.loss

            # 💡 Scaler를 통한 안전한 역전파
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()

            total_loss += loss.item()
            progress_bar.set_postfix({'loss': f"{loss.item():.4f}"})

        avg_loss = total_loss / len(dataloader)
        print(f"✅ Epoch {epoch+1} 완료! 평균 Loss: {avg_loss:.4f}")

    print("💾 학습된 모델을 저장합니다...")
    model.save_pretrained(SAVE_DIR)
    processor.save_pretrained(SAVE_DIR)
    print(f"🎉 성공적으로 저장되었습니다: {SAVE_DIR}")

if __name__ == "__main__":
    train_model()