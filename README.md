**Project Name:** Smart Caregiving Medicine Box for the Elderly Based on Face Recognition, MQTT, and Speech Synthesis

**Project Description:**
- This project aims to help elderly individuals take their medication on time and as prescribed, preventing issues such as missed doses, overdoses, or forgetting to take medication.
- It innovatively uses face recognition technology to verify the identity of the person taking the medication, not only to record the elderly person's medication adherence but also to prevent other family members or children from accidentally taking the medicine.
- **Technology Stack:**
  - **Development Board:** UNIHIKER
  - **Programming Language:** Python 3
  - **Computer Vision:** OpenCV (for image capture, recognition, and processing)
  - **IoT Communication:** MQTT protocol, SIoT server (for data transmission between devices)
  - **Development Tools:** Mind+, Python environment

- **Environment Preparation:**
  1. **Hardware Preparation**
    - 2 x UNIHIKER boards
    - 1 x Arduino development board
    - 3 x stepper motors
    - 3 x ultrasonic sensors
    - USB cable (for power supply and debugging)
    - 720P camera (built-in camera on UNIHIKER or external USB camera for visual capture)
    - 1 x computer (for writing and uploading code)

  2. **Software Preparation**
    - **Development Tool:** Mind+ (recommended, compatible with UNIHIKER, supports both drag-and-drop and code-based development)
    - **MQTT Server:** SIoT (official from DFRobot, lightweight and easy to deploy, compatible with UNIHIKER)
    - **Dependency Libraries:** OpenCV-Python, paho-mqtt (pre-installed on UNIHIKER), pywebio, datetime, time, re, unihiker (UNIHIKER control library), json, os, threading
    - **Environment Configuration:** Ensure that the UNIHIKER board and the computer are connected to the same Wi-Fi (local area network), and turn off the computer's firewall (to avoid blocking MQTT ports)

**Quick Start**
