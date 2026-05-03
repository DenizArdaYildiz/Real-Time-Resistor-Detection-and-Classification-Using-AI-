import argparse
from pathlib import Path
from ultralytics import YOLO
import cv2
import sys
import time
import os
import torch
import numpy as np # mss çıktısını OpenCV formatına dönüştürmek için
import mss # Ekran yakalama için
import mss.tools
import serial # Arduino ile haberleşme için eklendi

# --- Ayarlar ve Varsayılanlar ---
DEFAULT_DETECTION_MODEL_PATH = "models/DET_BEST.pt"
DEFAULT_CLASSIFICATION_MODEL_PATH = "models/CLS_BEST.pt"

DETECTION_CONF_THRESHOLD_DEFAULT = 0.50
CLASSIFICATION_CONF_THRESHOLD_DEFAULT = 0.60

OHM_TO_DISPLAY_MAP = {
    320: "0",
    330: "1",
    1000: "2",
    1500: "3",
    2200: "4",
    3300: "5",
    4700: "6",
    10000: "7",
    100000: "8",
    1000000: "9"
}

# --- Seri Port Ayarları (Arduino için) ---
SERIAL_PORT_DEFAULT = 'COM3'  # <--- DİKKAT: BU DEĞERİ KENDİ SİSTEMİNİZE GÖRE DEĞİŞTİRİN!
                                # Windows'ta "COM3", "COM4" vb.
                                # Linux/macOS'ta "/dev/ttyUSB0", "/dev/ttyACM0" vb. olabilir.
BAUD_RATE = 9600
ser = None # Seri bağlantı nesnesi
# ---------------

def check_display_available():
    return os.environ.get('DISPLAY') is not None or sys.platform in ['win32', 'darwin']

def get_scrcpy_window_region(sct):
    print("\n--- SCRCPY Pencere Bölgesi Ayarı ---")
    print("Lütfen scrcpy pencerenizi konumlandırın.")
    print("Yakalama bölgesini (üst, sol, genişlik, yükseklik) tanımlamanız gerekiyor.")
    print("Alternatif olarak, scrcpy'yi tam ekran yaparsanız birincil monitörün tamamını yakalayabilirsiniz.")

    choice = input("Birincil monitörün [T]amamını mı yoksa [B]elirli bir bölgeyi mi yakalamak istersiniz? (T/B): ").strip().lower()

    if choice == 'b':
        print("scrcpy penceresinin bölgesini tanımlayın (piksel cinsinden):")
        try:
            top = int(input("  Üst (top): "))
            left = int(input("  Sol (left): "))
            width = int(input("  Genişlik (width): "))
            height = int(input("  Yükseklik (height): "))
            if width <= 0 or height <= 0:
                print("HATA: Genişlik ve yükseklik pozitif olmalıdır. Çıkılıyor.")
                sys.exit(1)
            return {"top": top, "left": left, "width": width, "height": height, "monitor_number": None}
        except ValueError:
            print("HATA: Geçersiz sayısal giriş. Çıkılıyor.")
            sys.exit(1)
    else:
        monitors = sct.monitors
        print("Algılanan Monitörler:")
        for i, monitor in enumerate(monitors):
            print(f"  {i}: {monitor}")
        default_monitor_index = 1 if len(monitors) > 1 else 0
        monitor_number_to_use = default_monitor_index
        try:
            monitor_input = input(f"Yakalanacak monitör numarasını girin (varsayılan: {default_monitor_index} - genellikle birincil monitör): ").strip()
            if monitor_input:
                selected_index = int(monitor_input)
                if 0 <= selected_index < len(monitors):
                    monitor_number_to_use = selected_index
                else:
                    print(f"Geçersiz monitör numarası. Varsayılan monitör ({default_monitor_index}) kullanılacak.")
        except ValueError:
            print(f"Geçersiz giriş. Varsayılan monitör ({default_monitor_index}) kullanılacak.")
        print(f"Monitör {monitor_number_to_use} yakalanacak: {monitors[monitor_number_to_use]}")
        return monitors[monitor_number_to_use]


def run_resistor_prediction(
    det_model_path_str,
    cls_model_path_str,
    input_source="camera",
    camera_index=0,
    show_window=True,
    det_conf=0.5,
    cls_conf=0.6,
    serial_port_to_use=SERIAL_PORT_DEFAULT
):
    global ser

    print("-" * 30)
    print(f"Tespit Modeli:        {det_model_path_str}")
    print(f"Sınıflandırma Modeli:  {cls_model_path_str}")
    print(f"Giriş Kaynağı:        {input_source}")
    if input_source == "camera":
        print(f"Kamera Index'i:       {camera_index}")
    print(f"Arduino Seri Port:    {serial_port_to_use}")
    print(f"Tespit Güven Eşiği:   {det_conf}")
    print(f"Sınıf. Güven Eşiği:  {cls_conf}")

    det_model_path = Path(det_model_path_str)
    cls_model_path = Path(cls_model_path_str)

    if not det_model_path.is_file():
        print(f"\nHATA: Tespit model dosyası bulunamadı: {det_model_path}")
        sys.exit(1)
    if not cls_model_path.is_file():
        print(f"\nHATA: Sınıflandırma model dosyası bulunamadı: {cls_model_path}")
        sys.exit(1)

    try:
        ser = serial.Serial(serial_port_to_use, BAUD_RATE, timeout=1)
        print(f"\nArduino ile {serial_port_to_use} @ {BAUD_RATE}bps portundan bağlantı kuruldu.")
        time.sleep(2)
    except serial.SerialException as e:
        print(f"HATA: Arduino ile seri bağlantı kurulamadı ({serial_port_to_use}): {e}")
        print("Seri bağlantı olmadan devam edilecek (Arduino'ya veri gönderilmeyecek).")
        ser = None

    device = 0 if torch.cuda.is_available() else "cpu"
    if device == "cpu":
        print("UYARI: CUDA (GPU) bulunamadı, CPU kullanılacak. Performans düşebilir.")
    else:
        try:
            print(f"CUDA (GPU) bulundu, {torch.cuda.get_device_name(device)} kullanılacak.")
        except Exception as e:
            print(f"CUDA (GPU) bulundu, ancak cihaz adı alınamadı: {e}. GPU kullanılacak.")
            device = 0

    cap = None
    sct = None
    capture_region = None

    try:
        print("\nModeller yükleniyor...")
        detection_model = YOLO(det_model_path)
        classification_model = YOLO(cls_model_path)
        print("Modeller başarıyla yüklendi.")

        can_display = check_display_available() and show_window
        if show_window and not can_display:
            print("UYARI: Görüntüleme ortamı algılanamadı/desteklenmiyor. Pencere gösterilmeyecek.")
        elif not show_window:
            print("Görüntüleme penceresi komutla kapatıldı (--no-show).")

        if input_source == "camera":
            print("\nKamera açılıyor...")
            cap = cv2.VideoCapture(camera_index)
            if not cap.isOpened():
                print(f"\nHATA: Kamera {camera_index} açılamadı.")
                sys.exit(1)
            print("Kamera açıldı.")
        elif input_source == "scrcpy":
            print("\nscrcpy ekran yakalama başlatılıyor...")
            try:
                sct = mss.mss()
                capture_region = get_scrcpy_window_region(sct)
                if not capture_region or capture_region.get("width", 0) == 0 or capture_region.get("height", 0) == 0:
                    print("HATA: Geçersiz scrcpy yakalama bölgesi.")
                    sys.exit(1)
                print(f"scrcpy yakalama bölgesi ayarlandı: {capture_region}")
            except Exception as e:
                print(f"\nHATA: mss (ekran yakalama) başlatılamadı: {e}")
                sys.exit(1)
        else:
            print(f"\nHATA: Geçersiz giriş kaynağı: {input_source}. 'camera' veya 'scrcpy' kullanın.")
            sys.exit(1)

        window_name = "Direnc Okuyucu - Durdur: q"
        if can_display:
            print(f"Durdurmak için '{window_name}' penceresi aktifken 'q' tuşuna basın.")
        else:
            print("Durdurmak için konsolda Ctrl+C yapın.")

        while True:
            frame = None
            if input_source == "camera":
                ret, frame_read = cap.read()
                if not ret:
                    print("\nHATA: Kameradan kare okunamadı, çıkılıyor.")
                    time.sleep(2)
                    break
                frame = frame_read
            elif input_source == "scrcpy" and sct and capture_region:
                sct_img = sct.grab(capture_region)
                frame = np.array(sct_img)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

            if frame is None:
                print("HATA: Kare alınamadı.")
                time.sleep(0.1)
                continue
            if frame.shape[0] == 0 or frame.shape[1] == 0:
                print("HATA: Boş kare alındı, atlanıyor.")
                time.sleep(0.1)
                continue

            det_results = detection_model.predict(frame, conf=det_conf, verbose=False, device=device)

            if det_results and det_results[0].boxes:
                for box in det_results[0].boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cropped_resistor = frame[y1:y2, x1:x2]

                    if cropped_resistor.size == 0:
                        continue

                    cls_results = classification_model.predict(cropped_resistor, conf=cls_conf, verbose=False, device=device)
                    display_text_on_frame = "Bilinmiyor"
                    arduino_data_to_send = None

                    if cls_results and cls_results[0].probs is not None:
                        top1_prob = cls_results[0].probs.top1conf.item()
                        predicted_class_idx = cls_results[0].probs.top1
                        predicted_ohm_str = classification_model.names[predicted_class_idx]

                        try:
                            predicted_ohm_int = int(predicted_ohm_str)
                            arduino_data_to_send = OHM_TO_DISPLAY_MAP.get(predicted_ohm_int)
                            
                            display_text_val_for_screen = OHM_TO_DISPLAY_MAP.get(predicted_ohm_int, f"{predicted_ohm_int}Ω")
                            display_text_on_frame = f"{display_text_val_for_screen} ({top1_prob:.2f})"

                            if arduino_data_to_send is not None and ser and ser.is_open:
                                try:
                                    ser.write(arduino_data_to_send.encode('utf-8'))
                                    print(f"Arduino'ya gönderildi: {arduino_data_to_send}") # Konsolda göster
                                except serial.SerialException as e:
                                    print(f"Arduino'ya yazma hatası: {e}")
                                except Exception as e_gen:
                                    print(f"Arduino'ya veri gönderirken genel hata: {e_gen}")
                        except ValueError:
                            display_text_on_frame = f"Hata: {predicted_ohm_str} ({top1_prob:.2f})"
                    
                    if can_display:
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        label_y_pos = y1 - 10 if y1 - 10 > 10 else y1 + 20
                        cv2.putText(frame, display_text_on_frame, (x1, label_y_pos),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2, cv2.LINE_AA) 
                        cv2.putText(frame, display_text_on_frame, (x1, label_y_pos),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (50, 255, 50), 1, cv2.LINE_AA)

            if can_display:
                cv2.imshow(window_name, frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("\n'q' tuşuna basıldı, durduruluyor.")
                    break
            else:
                time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nCtrl+C algılandı. Program sonlandırılıyor.")
    except Exception as e:
        print(f"\nGenel bir hata oluştu: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if cap and cap.isOpened():
            cap.release()
            print("\nKamera kapatıldı.")
        if sct:
            sct.close()
            print("\nEkran yakalama durduruldu.")
        if ser and ser.is_open:
            ser.close()
            print("\nSeri port kapatıldı.")
        
        if can_display and 'window_name' in locals():
            try:
                if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) >= 1:
                    cv2.destroyAllWindows()
            except cv2.error as e:
                print(f"OpenCV penceresi kapatılırken hata oluştu (görmezden gelinebilir): {e}")
        print("Kaynaklar temizlendi.")
        print("-" * 30)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YOLOv8 ile Canlı Direnç Tespiti, Değer Okuma ve Arduino Kontrolü")
    parser.add_argument('--input_source', type=str, default="camera", choices=['camera', 'scrcpy'],
                        help="Giriş kaynağı: 'camera' veya 'scrcpy' (varsayılan: camera)")
    parser.add_argument('--det_model', type=str, default=DEFAULT_DETECTION_MODEL_PATH,
                        help=f"Kullanılacak .pt tespit model dosyasının yolu (varsayılan: {DEFAULT_DETECTION_MODEL_PATH})")
    parser.add_argument('--cls_model', type=str, default=DEFAULT_CLASSIFICATION_MODEL_PATH,
                        help=f"Kullanılacak .pt sınıflandırma model dosyasının yolu (varsayılan: {DEFAULT_CLASSIFICATION_MODEL_PATH})")
    parser.add_argument('--camera', type=int, default=0,
                        help="Kullanılacak kamera index'i (input_source 'camera' ise kullanılır)")
    parser.add_argument('--no-show', action='store_true',
                        help="Görüntüleme penceresini açmayı deneme")
    parser.add_argument('--det_conf', type=float, default=DETECTION_CONF_THRESHOLD_DEFAULT,
                        help=f"Tespit için minimum güven eşiği (varsayılan: {DETECTION_CONF_THRESHOLD_DEFAULT})")
    parser.add_argument('--cls_conf', type=float, default=CLASSIFICATION_CONF_THRESHOLD_DEFAULT,
                        help=f"Sınıflandırma için minimum güven eşiği (varsayılan: {CLASSIFICATION_CONF_THRESHOLD_DEFAULT})")
    parser.add_argument('--serial_port', type=str, default=SERIAL_PORT_DEFAULT,
                        help=f"Arduino için seri port (varsayılan: {SERIAL_PORT_DEFAULT})")
    
    args = parser.parse_args()

    run_resistor_prediction(
        args.det_model, 
        args.cls_model, 
        input_source=args.input_source,
        camera_index=args.camera, 
        show_window=not args.no_show,
        det_conf=args.det_conf,
        cls_conf=args.cls_conf,
        serial_port_to_use=args.serial_port
    )