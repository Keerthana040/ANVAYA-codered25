import cv2
import os
import numpy as np

def prepare_training_data(dataset_path):
    faces = []
    labels = []
    label_map = {}
    current_label = 0

    # Loop through each person in the dataset folder
    for person_name in os.listdir(dataset_path):
        person_path = os.path.join(dataset_path, person_name)
        if not os.path.isdir(person_path):
            continue

        # Map label to person name (Ensure your folder names are exactly the names you want)
        label_map[current_label] = person_name

        # Loop through each image for the person
        for filename in os.listdir(person_path):
            filepath = os.path.join(person_path, filename)
            img = cv2.imread(filepath)
            if img is None:
                print(f"Warning: Could not read image {filepath}")
                continue

            # Convert to grayscale and resize to a consistent size (100x100)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            gray = cv2.resize(gray, (100, 100))  # Resize for consistency

            faces.append(gray)
            labels.append(current_label)

        print(f"Processed images for {person_name} (Label: {current_label})")
        current_label += 1

    print("Label Map:", label_map)  # Debugging output to ensure proper mapping
    return faces, labels, label_map

# Main code to train the model
dataset_path = r"D:\FACIAL RECOG\known_faces"  # Path to your dataset

faces, labels, label_map = prepare_training_data(dataset_path)

# Check that we have data
if len(faces) == 0:
    print("Error: No faces found for training.")
else:
    # Train the LBPH Face Recognizer
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(faces, np.array(labels))

    # Save the trained model to a file
    recognizer.save("face_trainer.yml")
    print("Training complete. Model saved as face_trainer.yml")

    # Optionally, you can also print the label map to verify the training
    print("Label map for training:")
    for label, name in label_map.items():
        print(f"Label {label} corresponds to {name}")
