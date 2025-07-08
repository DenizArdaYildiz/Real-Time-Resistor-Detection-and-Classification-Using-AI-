# 🔍 Real-Time Resistor Detection and Classification Using AI & Arduino

This project combines **computer vision**, **machine learning**, and **Arduino-based hardware control** to detect resistors, read their color bands, classify their resistance values, and sort them in real time.

---

## 🧠 Project Summary

- Uses a YOLOv8 model to **detect resistor positions** in video or screen input.
- Crops detected resistor regions and classifies **color bands** using a custom-trained classification model.
- Sends the resistance value to **Arduino** via serial communication.
- Arduino moves a **stepper motor or servo** to sort or position the resistor.

---

## 🖼️ Input & Output

- **Input**: Video stream (e.g., webcam or screen capture)
- **Output**: Detected resistor with bounding box + predicted resistance (e.g., “10 kΩ”)
- **Hardware**: Arduino receives resistance info and controls mechanism to sort/move resistors.

---

## ⚙️ Components

- **YOLOv8 Detection Model (`DET_BEST.pt`)**  
  Detects location of resistors in the image.

- **Classification Model (`CLS_BEST.pt`)**  
  Classifies the resistor’s band pattern into discrete resistance values.

- **Arduino Microcontroller**  
  Receives serial input from Python and executes physical movement (e.g., servo, motor).

---

## 🧪 How It Works

1. Capture live image or video.
2. Use YOLOv8 to detect resistor.
3. Crop the detected area and send to classification model.
4. Predict resistance label (e.g., 220Ω, 1kΩ, etc.).
5. Display prediction on screen.
6. Send result to Arduino via serial port (e.g., COM3).
7. Arduino activates mechanical system to handle the resistor.

---

## 📦 Installation

```bash
pip install ultralytics opencv-python torch serial
```

Ensure YOLOv8 weights and classifier weights are in your working directory.

---

## ▶️ Running the System

```bash
python direnç.ipynb
```

Or convert to `.py` and run with:

```bash
python detect_resistor.py
```

Make sure:
- Arduino is connected and listening via serial
- `DET_BEST.pt` and `CLS_BEST.pt` are available
- Correct COM port is set (e.g., `serial.Serial('COM3', 9600)`)

---

## 📂 Folder Structure

```
resistor_ai_sorter/
├── direnç.ipynb
├── DET_BEST.pt
├── CLS_BEST.pt
├── arduino/
│   └── servo_control.ino
├── outputs/
│   └── detected_frames/
└── README.md
```

---

## 💡 Future Ideas

- Improve classification accuracy with larger dataset
- Add GUI for manual override
- Log all resistance values for inventory tracking
- Use camera calibration to improve ROI cropping

---

## 👨‍💻 Author

Deniz Arda YILDIZ  
Email: [denizarda.yildiz@protonmail.com]  


---

## 📝 License

This project is open-source and available under the MIT License.
