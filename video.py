import easyocr
import cv2
import os
import numpy as np

# Türkçe dil desteğiyle OCR okuyucu
reader = easyocr.Reader(['tr'])

# Video dosyasının varlığını kontrol et
video_path = 'video.mp4'
if not os.path.exists(video_path):
    print(f"Hata: {video_path} dosyası bulunamadı!")
    exit()

cap = cv2.VideoCapture(video_path)

# Video özelliklerini al
fps = cap.get(cv2.CAP_PROP_FPS)
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
print(f"Video FPS: {fps}")
print(f"Toplam frame sayısı: {total_frames}")

# Çıktı dosyasını oluştur ve aç
output_file = "output.txt"
with open(output_file, "w", encoding="utf-8") as file:
    frame_count = 0
    text_count = 0
    previous_frame = None
    previous_texts = set()
    frame_interval = int(fps*10)  # Her 10 saniye için bir frame
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        frame_count += 1

         # Sadece belirli frame'leri işle (saniyede bir)
        if frame_count % frame_interval != 0:
            continue
        current_time = frame_count / fps  # Saniye cinsinden süre
        current_time_formatted = f"{int(current_time // 60):02d}:{int(current_time % 60):02d}"  # MM:SS formatı
        
        # Frame'leri karşılaştır
        if previous_frame is not None:
            # Frame'ler arasındaki farkı hesapla
            diff = cv2.absdiff(frame, previous_frame)
            diff_sum = np.sum(diff)
            
            # Eğer frame'ler çok benzer ise atla
            if diff_sum < 100000:
                print(f"Frame {frame_count} ({current_time_formatted}) benzer, atlanıyor...")
                continue
        
        print(f"Frame {frame_count} ({current_time_formatted}) işleniyor...")

        # OCR işlemi
        result = reader.readtext(frame)
        current_texts = set()
        
        for detection in result:
            text = detection[1]
            current_texts.add(text)
            
            # Eğer bu metin daha önce görülmediyse yaz
            if text not in previous_texts:
                text_count += 1
                print(f"Tespit edilen yeni metin {text_count} [{current_time_formatted}]: {text}")
                file.write(f"[{current_time_formatted}] {text}\n")
                file.flush()
        
        # Güncellemeler
        previous_frame = frame.copy()
        previous_texts = current_texts

cap.release()
print(f"\nİşlem tamamlandı:")
print(f"- İşlenen frame sayısı: {frame_count}/{total_frames}")
print(f"- Tespit edilen benzersiz metin sayısı: {text_count}")
print(f"- Metinler '{output_file}' dosyasına yazıldı.")
