import cv2
import mediapipe as mp
import math
import winsound
import os
import pandas as pd
import requests
from datetime import datetime
from dotenv import load_dotenv

#for security reasons
load_dotenv()

sid = os.getenv(
    "TWILIO_ACCOUNT_SID"
)

token = os.getenv(
    "TWILIO_AUTH_TOKEN"
)

webhook_url = os.getenv(
    "WEBHOOK_URL"
)
# --------------------------
# START CAMERA
# --------------------------

camera = cv2.VideoCapture(0)

# --------------------------
# MEDIAPIPE FACE MESH
# --------------------------

mp_face_mesh = mp.solutions.face_mesh

face_mesh = mp_face_mesh.FaceMesh(
    refine_landmarks=True
)

# --------------------------
# VARIABLES
# --------------------------

sleep_counter = 0
screenshot_taken = False
status = "AWAKE"

# --------------------------
# N8N WEBHOOK URL
# --------------------------

# --------------------------
# MAIN LOOP
# --------------------------

while True:

    success, frame = camera.read()

    if not success:
        break

    # Flip camera
    frame = cv2.flip(frame, 1)

    # from BGR to RGB convertion
    rgb_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    # Process face
    results = face_mesh.process(
        rgb_frame
    )

    # Face detected
    if results.multi_face_landmarks:

        for face_landmarks in results.multi_face_landmarks:

            # Eye landmarks
            top = 159
            bottom = 145
            left = 33
            right = 133

            # Landmark points
            top_point = face_landmarks.landmark[top]
            bottom_point = face_landmarks.landmark[bottom]
            left_point = face_landmarks.landmark[left]
            right_point = face_landmarks.landmark[right]

            # Frame size
            h, w, _ = frame.shape

            # Convert to pixel coordinates
            top_x, top_y = int(top_point.x * w), int(top_point.y * h)
            bottom_x, bottom_y = int(bottom_point.x * w), int(bottom_point.y * h)

            left_x, left_y = int(left_point.x * w), int(left_point.y * h)
            right_x, right_y = int(right_point.x * w), int(right_point.y * h)

            # Draw eye points
            cv2.circle(frame, (top_x, top_y), 3, (0,255,0), -1)
            cv2.circle(frame, (bottom_x, bottom_y), 3, (0,255,0), -1)
            cv2.circle(frame, (left_x, left_y), 3, (0,255,0), -1)
            cv2.circle(frame, (right_x, right_y), 3, (0,255,0), -1)

            # Eye distances
            vertical_distance = math.hypot(
                top_x - bottom_x,
                top_y - bottom_y
            )

            horizontal_distance = math.hypot(
                left_x - right_x,
                left_y - right_y
            )

            # Eye ratio
            eye_ratio = (
                vertical_distance /
                horizontal_distance
            )

            # Detect sleep
            if eye_ratio < 0.22:
                sleep_counter += 1
                status = "SLEEPY"

            else:
                sleep_counter = 0
                status = "AWAKE"
                screenshot_taken = False

            # Sleep Alert
            if sleep_counter > 35:

                cv2.putText(
                    frame,
                    "SLEEP ALERT!",
                    (100,100),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0,0,255),
                    3
                )

                # Alarm
                winsound.Beep(1000, 500)

                # Save screenshot
                if not screenshot_taken:

                    current_time = datetime.now().strftime(
                        "%Y-%m-%d_%H-%M-%S"
                    )

                    filename = (
                        f"screenshots/sleep_{current_time}.jpg"
                    )

                    cv2.imwrite(
                        filename,
                        frame
                    )

                    print(
                        "Screenshot Saved:",
                        filename
                    )

                    # Save CSV Report
                    report = pd.DataFrame([{
                        "Date": datetime.now().strftime("%Y-%m-%d"),
                        "Time": datetime.now().strftime("%I:%M:%S %p"),
                        "Status": "Sleep Detected",
                        "Screenshot": filename
                    }])

                    report.to_csv(
                        "driver_report.csv",
                        mode="a",
                        header=False,
                        index=False
                    )

                    print("Report Saved")

                    # Send n8n webhook
                    try:

                        data = {
                            "status": "Sleep Detected",
                            "time": datetime.now().strftime(
                                "%I:%M:%S %p"
                            )
                        }

                        response = requests.post(
                            webhook_url,
                            json=data
                        )

                        print(
                            "Webhook Sent:",
                            response.status_code
                        )

                    except Exception as e:
                        print(
                            "Webhook Error:",
                            e
                        )

                    screenshot_taken = True

    # Status UI
    cv2.putText(
        frame,
        f"STATUS: {status}",
        (20,50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0,255,0),
        2
    )

    # Sleep counter
    cv2.putText(
        frame,
        f"Sleep Frames: {sleep_counter}",
        (20,90),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255,255,255),
        2
    )

    # Show window
    cv2.imshow(
        "AI Driver Sleep Detection",
        frame
    )

    # ESC key to exit
    if cv2.waitKey(1) == 27:
        break

# Close everything
camera.release()
cv2.destroyAllWindows()