import torch
import cv2
import numpy as np

# Load the YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
model.conf = 0.5  # Confidence threshold to reduce unnecessary detections

# Enable half-precision for GPU inference
if torch.cuda.is_available():
    model.half()

# Initialize the video capture (webcam)
video = cv2.VideoCapture(0)  # Use 0 for default webcam
if not video.isOpened():
    print("Error: Could not open webcam.")
    exit()

print("Press 'q' to quit.")

while True:
    ret, frame = video.read()
    if not ret:
        print("Error: Could not read frame.")
        break

    # Resize frame to speed up detection
    resized_frame = cv2.resize(frame, (640, 480))

    # Convert frame to RGB (YOLOv5 requires RGB input)
    rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)

    # Perform object detection
    with torch.no_grad():  # Disable gradient calculation for inference
        results = model(rgb_frame)

    # Extract bounding boxes, confidence scores, and class labels
    # Access the .xyxy attribute to get the bounding boxes
    detections = results.xyxy[0].cpu().numpy()  # Format: (xmin, ymin, xmax, ymax, confidence, class)

    for detection in detections:
        xmin, ymin, xmax, ymax, confidence, class_id = detection
        label = f"{results.names[int(class_id)]} {confidence:.2f}"

        # Filter detections based on proximity (bounding box size heuristic)
        bbox_width = xmax - xmin
        bbox_height = ymax - ymin
        if bbox_width > 50 and bbox_height > 50:  # Adjust thresholds for your camera and setup
            # Draw the bounding box
            cv2.rectangle(frame, (int(xmin), int(ymin)), (int(xmax), int(ymax)), (0, 255, 0), 2)
            cv2.putText(frame, label, (int(xmin), int(ymin) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Display the output frame
    cv2.imshow("YOLOv5 Object Detection", frame)

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Exiting...")
        break

# Release resources
video.release()
cv2.destroyAllWindows()

# Print the list of classes YOLO can detect
print(model.names)
