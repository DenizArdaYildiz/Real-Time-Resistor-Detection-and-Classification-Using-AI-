# 🔌 Real-Time Resistor Detection & Classification System (YOLOv8 + Arduino)

## 📌 Overview

This project implements an **end-to-end real-time computer vision system** for detecting and classifying resistor values using deep learning. The system integrates **YOLOv8-based object detection and classification models** with an **Arduino-controlled hardware setup** via serial communication.

The pipeline enables automatic resistor value recognition and can be extended to **embedded electronics applications** such as sorting, display systems, or robotic control.

---

## ⚙️ Features

* 🔍 Real-time resistor detection using YOLOv8
* 🧠 Resistor value classification (Ohm prediction)
* 📷 Supports live camera and screen input (scrcpy)
* 🔗 Serial communication with Arduino
* ⚡ End-to-end pipeline from vision → hardware control
* 🖥️ GPU acceleration support (CUDA)

---

## 🧠 System Pipeline

```
Camera / Screen Input
        ↓
YOLOv8 Detection Model
        ↓
Crop Detected Resistor
        ↓
YOLOv8 Classification Model
        ↓
Ohm Value Mapping
        ↓
Serial Communication
        ↓
Arduino Control (Display / Motor / Output)
```

---

## 🛠️ Tech Stack

* Python
* PyTorch
* YOLOv8 (Ultralytics)
* OpenCV
* NumPy
* MSS (screen capture)
* Arduino (Serial Communication)

---

## 📂 Project Structure

```
.
├── arduino/
│   └── arduino_step_kontrol.ino
├── src/
│   └── predict_resistors_serial.py
├── training/
│   └── train.ipynb
├── models/
│   ├── DET_BEST.pt
│   └── CLS_BEST.pt
└── README.md
```

---

## 🚀 How It Works

1. The system captures frames from a **camera or screen**
2. YOLOv8 detects resistor locations
3. Detected regions are cropped
4. A classification model predicts resistor values
5. The predicted value is mapped to a digit
6. Data is sent to Arduino via serial communication
7. Arduino performs a physical action (e.g. display or motor control)

---

## 🔌 Arduino Integration

* Python sends predicted resistor values via serial port
* Arduino reads incoming data and executes corresponding actions
* Example use cases:

  * 7-segment display output
  * Stepper motor control
  * Automated resistor sorting

Arduino code is available in the `/arduino` directory.

---

## ▶️ Usage

### 1. Install dependencies

```
pip install ultralytics opencv-python numpy torch mss pyserial
```

### 2. Run the system

```
python predict_resistors_serial.py --input_source camera
```

### Optional parameters

```
--input_source camera | scrcpy
--det_model path_to_detection_model
--cls_model path_to_classification_model
--serial_port COM3
```

---

## 📊 Training

Model training is provided in:

```
training/train.ipynb
```

Includes:

* Dataset preprocessing
* Model training
* Evaluation

---

## 📈 Future Improvements

* Improve classification accuracy
* Add multi-object tracking
* Deploy on edge devices (Jetson / Raspberry Pi)
* Extend to full electronic component recognition

---

## 👨‍💻 Author

**Deniz Arda Yildiz**

---

## ⭐ Notes

This project demonstrates a **real-world AI system combining deep learning with hardware integration**, going beyond standard model training by enabling physical interaction through embedded systems.
