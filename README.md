🔌 Real-Time Resistor Detection & Classification System (YOLOv8 + Arduino)
📌 Overview

This project presents a real-time computer vision system for detecting and classifying resistor values using deep learning. It integrates YOLOv8-based object detection and classification models with an Arduino-controlled hardware system via serial communication.

The system demonstrates a complete pipeline from image acquisition to physical hardware interaction, making it suitable for applications such as automated resistor sorting, embedded systems, and smart electronics.

⚙️ Features
🔍 Real-time resistor detection using YOLOv8
🧠 Resistor value classification (Ohm prediction)
📷 Supports camera and screen input (scrcpy)
🔗 Serial communication with Arduino
⚡ End-to-end AI + hardware pipeline
🖥️ GPU support (CUDA)
🧠 System Pipeline
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
Arduino Control (Display / Motor / Output)
🛠️ Tech Stack
Python
PyTorch
YOLOv8 (Ultralytics)
OpenCV
NumPy
MSS (screen capture)
Arduino (Serial Communication)
📂 Project Structure
.
├── README.md
├── arduino_step_kontrol.ino
├── predict_resistors_serial.py
├── train.ipynb
└── models/ (not included)
🚀 Usage
1. Install dependencies
pip install ultralytics opencv-python numpy torch mss pyserial
2. Run the system
python predict_resistors_serial.py --input_source camera
Optional parameters
--input_source camera | scrcpy
--det_model path_to_detection_model
--cls_model path_to_classification_model
--serial_port COM3
📊 Dataset

The dataset used in this project was manually collected and annotated.

Due to data loss and/or usage constraints, the dataset is not publicly available.
However, the system is designed to be easily adaptable to custom datasets.

📦 Models

Due to GitHub file size limitations, pretrained models are not included in this repository.

You can:

Train your own models using train.ipynb
Place trained models inside a models/ directory
🔌 Arduino Integration

The system communicates with an Arduino via serial port:

Python sends predicted resistor values
Arduino receives and processes the data
Hardware actions can include:
Display output
Stepper motor control
Automated sorting systems
📈 Future Improvements
Improve classification accuracy
Add multi-object tracking
Deploy on edge devices (Jetson / Raspberry Pi)
Extend to other electronic components
👨‍💻 Author

Deniz Arda Yildiz


⭐ Notes

This project demonstrates a real-world AI system combining deep learning with hardware integration, going beyond standard model training by enabling physical interaction through embedded systems.
