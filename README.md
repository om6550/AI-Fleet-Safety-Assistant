# AI Fleet Safety Assistant

## Project Overview

AI Fleet Safety Assistant is a computer vision based driver monitoring system.

The system detects driver drowsiness using face and eye tracking.

When sleep is detected:

- Alarm sound is activated
- Driver screenshot is captured
- Event is stored in CSV report
- WhatsApp alert is sent
- Emergency phone call is triggered

## Technologies Used

- Python
- OpenCV
- MediaPipe
- Pandas
- n8n
- Twilio
- Webhook API

## Features

- Real-time face detection
- Eye tracking
- Sleep detection
- Screenshot capture
- CSV logging
- WhatsApp notifications
- Automated phone calls

## Workflow

Camera
→ Face Detection
→ Eye Detection
→ Sleep Detection
→ Alarm
→ Screenshot
→ CSV
→ Webhook
→ n8n
→ Twilio
→ WhatsApp + Call

## Future Scope

- Android Application
- Fleet Dashboard
- GPS Tracking
- Driver Safety Score
