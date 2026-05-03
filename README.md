# 🔌 Real-Time Resistor Detection & Classification System (YOLOv8 + Arduino)

## 📌 Overview
This project presents a **real-time computer vision system** for detecting and classifying resistor values using deep learning. It integrates **YOLOv8-based object detection and classification models** with an **Arduino-controlled hardware system** via serial communication.

---

## ⚙️ Features
- Real-time resistor detection  
- Classification (Ohm prediction)  
- Camera / screen input  
- Arduino communication  
- End-to-end pipeline  

---

## 🧠 System Pipeline

```
Camera / Screen Input
        ↓
YOLOv8 Detection Model
        ↓
Crop Detected Resistor
        ↓
Classification Model
        ↓
Ohm Value Mapping
        ↓
Serial Communication
        ↓
Arduino Control
```

---

## 🛠️ Tech Stack
- Python  
- PyTorch  
- YOLOv8  
- OpenCV  
- NumPy  
- Arduino  

---

## 📂 Project Structure

```
.
├── README.md
├── arduino_step_kontrol.ino
├── predict_resistors_serial.py
├── train.ipynb
└── models/
```

---

## 🚀 Usage

```bash
pip install ultralytics opencv-python numpy torch mss pyserial
python predict_resistors_serial.py --input_source camera
```

---

## 📊 Dataset
Custom collected dataset (not publicly available).

---

## 📦 Models
Models are not included due to size limits. Train using `train.ipynb`.

---

## 🔌 Arduino
Python sends predictions → Arduino executes hardware actions.

---

## 👨‍💻 Author
Deniz Arda Yildiz
