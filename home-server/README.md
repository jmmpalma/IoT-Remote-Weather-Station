# IoT Remote Weather Station

This project is a full-stack IoT system designed to monitor environmental conditions and security events. It consists in two "moving parts", a remote field unit (Raspberry Pi Zero 2W) and a cloud-based data hub (Google Cloud Platform). 

## 📋 Project Overview
The system captures temperature, humidity, pressure, and motion data. When it detetcts motion, it takes a picture. This information is transmitted through a secure, private network to a database and visualized on a responsive web dashboard accessible from any authorized device.
The final version of this system aims to be fully autonomous, working solely with energy supplied by a solar panel.

## 🏗️ How It Is Being Done

### 1. Data Capture & Edge Logic
*   **Periodic Sampling:** A Raspberry Pi Zero 2W reads environmental data every 15 minutes.
*   **Event Handling:** A PIR sensor monitors for motion in real-time, and takes pictures when it detects motion. To prevent "data flooding," I implemented a rate-limiting algorithm that pauses alerts if too many triggers occur in a short window.

### 2. Secure Networking (Zero-Trust Architecture)
*   **Tailscale Mesh:** Instead of opening ports to the public internet, I used Tailscale to create a private, encrypted tunnel between the Pi, the Cloud VM, and my personal devices.
*   **MQTT Protocol:** Data is sent using the lightweight MQTT protocol (Mosquitto), which is the industry standard for IoT communication.

### 3. Cloud Infrastructure & Storage
*   **Database:** A PostgreSQL database running on a Google Cloud VM stores every sensor reading and system log permanently.
*   **Data Ingestion:** A Python-based "Listener" script runs 24/7 to catch incoming MQTT messages and sort them into the correct database tables.

### 4. Web Visualization
*   **Flask Dashboard:** A custom web server built with Flask provides a live UI.
*   **Dynamic Charts:** Uses Chart.js to display 24-hour trends for temperature and humidity using a dual-axis graph.
*   **System Monitoring:** The dashboard also tracks the Pi's CPU temperature and displays a live log of all system events.

### 5. Industrial Reliability
*   **Systemd Services:** All scripts (on both the Pi and the VM) are configured as Linux services. They start automatically on boot and restart themselves if a crash occurs.

## 🛠️ Tools & Components

### **Hardware**
*   **Raspberry Pi Zero 2W:** The central controller.
*   **BME280 Sensor:** High-precision sensor for Temp/Hum/Pressure via I2C.
*   **PIR Sensor:** Infrared motion detection.
*   **Keyes RGB LED:** Physical status indicator.
*   **Ethernet Cabling:** Used high-quality twisted-pair wiring to ensure signal stability over longer distances.

### **Software & Cloud**
*   **Google Cloud Platform (GCP):** Compute Engine VM.
*   **Languages:** Python 3.13, SQL, JavaScript, HTML, CSS.
*   **Networking:** Tailscale (WireGuard), Mosquitto (MQTT).
*   **Database:** PostgreSQL.
*   **Web Framework:** Flask.
*   **Hardware Control:** GPIO Zero and Adafruit CircuitPython libraries.

---
**Developer:** João M. M. Palma