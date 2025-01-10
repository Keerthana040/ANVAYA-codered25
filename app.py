from flask import Flask, render_template, request, jsonify
import os
import pyttsx3
import subprocess
import time
import speech_recognition as sr
from backend.facial_recognition import facial_recognition, model_train, known_faces  # Corrected import
from backend.navigation import get_directions, get_precise_location, validate_location
from backend.object_detection import detect_objects

app = Flask(__name__)

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Function to give voice feedback
def speak(text):
    engine.say(text)
    engine.runAndWait()


@app.route("/")
def index():
    return render_template("index.html")  # This would be the front-end page.

@app.route("/voice_command", methods=["POST"])
def voice_command():
    recognizer = sr.Recognizer()

    # Capture voice input from the user
    with sr.Microphone() as source:
        speak("What feature would you like to use? Navigation, object detection, or facial recognition?")
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        # Recognize the voice input
        command = recognizer.recognize_google(audio).lower()
        print(f"User said: {command}")

        if "navigation" in command:
            speak("You have chosen navigation. Please provide start and end locations.")
            return jsonify({"response": "Navigation requested"}), 200

        elif "object detection" in command:
            speak("You have chosen object detection. Please upload an image.")
            return jsonify({"response": "Object detection requested"}), 200

        elif "facial recognition" in command:
            speak("You have chosen facial recognition. Please upload an image.")
            return jsonify({"response": "Facial recognition requested"}), 200

        else:
            speak("Sorry, I did not understand your request. Please try again.")
            return jsonify({"response": "Unknown command"}), 400

    except sr.UnknownValueError:
        speak("Sorry, I could not understand the audio. Please try again.")
        return jsonify({"error": "Could not understand audio"}), 400

    except sr.RequestError:
        speak("Sorry, there was an issue with the speech service. Please try again later.")
        return jsonify({"error": "Speech recognition service failed"}), 500

@app.route("/start_navigation", methods=["POST"])
def start_navigation():
    data = request.json
    start_location = data.get("start_location")
    end_location = data.get("end_location")
    
    if not start_location or not end_location:
        return jsonify({"error": "Missing start or end location"}), 400

    validated_start = validate_location(start_location)
    validated_end = validate_location(end_location)
    
    if validated_start and validated_end:
        directions = get_directions(validated_start, validated_end)
        return jsonify({"directions": directions})
    else:
        return jsonify({"error": "Invalid locations"}), 400

@app.route("/start_object_detection", methods=["POST"])
def start_object_detection():
    image = request.files.get("image")
    
    if image:
        image_path = os.path.join("static", "uploaded_image.jpg")
        image.save(image_path)

        detected_objects = detect_objects(image_path)
        
        return jsonify({"detected_objects": detected_objects})
    else:
        return jsonify({"error": "No image uploaded"}), 400

@app.route("/start_facial_recognition", methods=["POST"])
def start_facial_recognition():
    image = request.files.get("image")
    
    if image:
        # Save the image temporarily to a path
        image_path = os.path.join("static", "uploaded_face_image.jpg")
        image.save(image_path)

        # Step 1: Train the facial recognition model first
        try:
            speak("Training the facial recognition model...")
            print("Training the facial recognition model...")
            subprocess.run(["python", "facial_recognition/model_train.py"], check=True)
            speak("Model training completed.")

        except subprocess.CalledProcessError as e:
            speak(f"Error in training the model: {e}")
            return jsonify({"error": "Model training failed"}), 500
        
        # Step 2: Run facial recognition
        recognized_faces = known_faces(image_path)  # Corrected to use `known_faces`
        
        return jsonify({"recognized_faces": recognized_faces})
    else:
        return jsonify({"error": "No image uploaded"}), 400

if __name__ == "__main__":
    app.run(debug=True)
