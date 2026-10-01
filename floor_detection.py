import cv2
import requests
import time

# -----------------------------
# CHANGE THESE TWO VALUES
# -----------------------------

FLOOR_NUMBER = 3  # Change this to 1, 2, or 3 based on laptop floor

MAIN_SERVER_URL = "http://192.168.1.105:5000/update"# Replace 192.168.1.10 with your main laptop IP address

# -----------------------------

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Camera not opening. Try changing VideoCapture(0) to VideoCapture(1)")
    exit()

face_model = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

last_sent_status = None
last_send_time = 0

while True:
    ret, frame = camera.read()

    if not ret:
        print("Camera not working")
        break

    frame = cv2.flip(frame, 1)
    frame = cv2.resize(frame, (640, 480))

    # Waiting area box
    x1, y1 = 160, 90
    x2, y2 = 480, 380

    waiting_area = frame[y1:y2, x1:x2]

    gray = cv2.cvtColor(waiting_area, cv2.COLOR_BGR2GRAY)

    faces = face_model.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(40, 40)
    )

    person_detected = len(faces) > 0

    # Draw face box
    for (x, y, w, h) in faces:
        cv2.rectangle(waiting_area, (x, y), (x + w, y + h), (0, 255, 0), 2)

    if person_detected:
        color = (0, 255, 0)
        status_text = f"FLOOR {FLOOR_NUMBER}: PERSON DETECTED"
    else:
        color = (0, 0, 255)
        status_text = f"FLOOR {FLOOR_NUMBER}: NO PERSON"

    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)

    cv2.putText(
        frame,
        "LIFT WAITING AREA",
        (x1, y2 + 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        color,
        2
    )

    cv2.putText(
        frame,
        status_text,
        (30, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        color,
        2
    )

    cv2.putText(
        frame,
        "Press Q to exit",
        (30, 450),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )

    # Send data only when status changes or every 3 seconds
    current_time = time.time()

    if person_detected != last_sent_status or current_time - last_send_time > 3:
        data = {
            "floor": FLOOR_NUMBER,
            "person_detected": person_detected
        }

        try:
            response = requests.post(MAIN_SERVER_URL, json=data, timeout=2)
            print("Sent:", data, "Response:", response.status_code)
        except Exception as e:
            print("Could not send data to server:", e)

        last_sent_status = person_detected
        last_send_time = current_time

    cv2.imshow(f"Floor {FLOOR_NUMBER} Person Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()