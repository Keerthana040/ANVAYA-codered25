import cv2
import numpy as np

# Load the face cascade and the trained recognizer
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read(r'C:\Users\User\anvaya_app\backend\facial_recognition\face_trainer.yml')  # Raw string
  # Use the full path

# Update label map (Ensure this matches your training setup)
label_map = {0: 'Apoorva', 1: 'Person2', 2: 'Person3'}  # Replace with your label_map

# Start webcam feed
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture frame.")
        break

    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces_detected = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))

    for (x, y, w, h) in faces_detected:
        # Draw rectangle around the face
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Predict the person’s label
        face = gray[y:y + h, x:x + w]
        face = cv2.resize(face, (100, 100))  # Resize to match training
        label, confidence = recognizer.predict(face)

        # Display only the name (no confidence or number of faces)
        if confidence < 60:  # Adjust the threshold if needed
            name = label_map.get(label, "Unknown")  # Map label to name
        else:
            name = "Unknown"

        # Display name
        cv2.putText(frame, name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    # Show the output in a window
    cv2.imshow("Face Recognition", frame)

    # Exit if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close the window
cap.release()
cv2.destroyAllWindows()
