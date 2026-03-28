Project Name: AI-Powered Medication Management Device

Project Introduction:
-- This project aims to help the elderly take medicine on time and as required, preventing safety issues such as missing doses, taking too much, or forgetting to take medicine
-- Pioneering use of face recognition technology to verify the identity of the person taking medicine, which can not only record the elderly's medication status but also prevent other elderly people or children in the family from taking medicine by mistake
-- Tech Stack: 
  - Development Board: UNIHIKER

  - Programming Language: Python 3

  - Computer Vision: OpenCV (for image acquisition, recognition, and processing)

  - IoT Communication: MQTT Protocol, SIoT Server (for data transmission between devices)

  - Development Tools: Mind+, Python Environment


-- Environment Preparation:
1. Hardware Preparation

- 2 UNIHIKER boards

- 1 Arduino development board

- 3 stepper motors

- 3 ultrasonic sensors

- USB data cable (for power supply and debugging)

- 720P camera (UNIHIKER built-in camera or external USB camera for visual acquisition)

- 1 computer (for writing and uploading code)

2. Software Preparation

- Development Tools: Mind+ (Recommended, compatible with UNIHIKER, drag-and-drop + code-based development)

- MQTT Server: SIoT (Officially from DFRobot, lightweight and easy to deploy, compatible with UNIHIKER)

- Dependencies: OpenCV-Python, paho-mqtt (pre-installed on UNIHIKER), pywebio, datetime, time, re, unihiker (UNIHIKER control library), json, os, threading


- Environment Configuration: Ensure UNIHIKER and computer are connected to the same Wi-Fi (LAN), turn off computer firewall (to avoid blocking MQTT port)

Quick Start
