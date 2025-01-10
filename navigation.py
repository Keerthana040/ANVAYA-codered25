import googlemaps
import pyttsx3
import speech_recognition as sr
import requests

# Initialize Google Maps API
API_KEY = "AIzaSyADCKiBcGWpx1dcOKFvR9pNWIzcpn7KhuQ"  # Replace with your actual API key
gmaps = googlemaps.Client(key=API_KEY)

# Initialize Speech Recognition
recognizer = sr.Recognizer()


def speak(text):
    """Speaks the provided text using a fresh instance of the engine."""
    try:
        temp_engine = pyttsx3.init()
        temp_engine.say(text)
        temp_engine.runAndWait()
        temp_engine.stop()
    except Exception as e:
        print(f"Error in TTS: {e}")


def get_precise_location():
    """Uses Google Geolocation API with IP-based fallback for better accuracy."""
    url = f"https://www.googleapis.com/geolocation/v1/geolocate?key={API_KEY}"
    
    try:
        response = requests.post(url, json={})
        location_data = response.json()

        if "location" in location_data:
            lat = location_data["location"]["lat"]
            lng = location_data["location"]["lng"]

            # Convert lat/lng to a human-readable address
            reverse_geocode_result = gmaps.reverse_geocode((lat, lng))
            if reverse_geocode_result:
                address = reverse_geocode_result[0]['formatted_address']
                print(f"Precise Location Detected: {address}")
                return address
        else:
            print("Geolocation API failed. Using IP-based location as fallback.")
        
        # Fallback: Get location from IP
        ip_response = requests.get("https://ipinfo.io/json")
        ip_data = ip_response.json()
        if "loc" in ip_data:
            lat, lng = map(float, ip_data["loc"].split(","))
            reverse_geocode_result = gmaps.reverse_geocode((lat, lng))
            if reverse_geocode_result:
                address = reverse_geocode_result[0]['formatted_address']
                print(f"IP-Based Location Detected: {address}")
                return address
    except requests.exceptions.RequestException as e:
        print(f"Network Error: {e}")

    return None


def validate_location(location):
    """Checks if Google Maps recognizes the given location. Suggests alternatives if not found."""
    try:
        geocode_result = gmaps.geocode(location)
        if geocode_result:
            return geocode_result[0]['formatted_address']
        
        # If no exact match, find close alternatives
        alternative_results = gmaps.places_autocomplete(location)
        if alternative_results:
            print("Did you mean one of these?")
            speak("I could not find the exact location. Did you mean one of these?")
            for idx, result in enumerate(alternative_results[:3], 1):
                print(f"{idx}. {result['description']}")
                speak(f"Option {idx}: {result['description']}")

            # Let the user select an option
            choice = get_voice_command("Please say the number of the correct option.")
            if choice and choice.isdigit():
                selected_idx = int(choice) - 1
                if 0 <= selected_idx < len(alternative_results):
                    return alternative_results[selected_idx]['description']
            
            speak("No valid choice selected. Please say your destination again.")
            return None
    except googlemaps.exceptions.ApiError as e:
        print(f"Google Maps API Error: {e}")
    
    return None


def get_voice_command(prompt):
    """Takes voice input from the user."""
    with sr.Microphone() as source:
        print(prompt)
        speak(prompt)
        
        try:
            audio = recognizer.listen(source, timeout=5)
            command = recognizer.recognize_google(audio)
            print(f"Detected Input: {command}")
            return command.lower()
        except sr.UnknownValueError:
            print("Could not understand the audio.")
            speak("Sorry, I couldn't understand. Please try again.")
        except sr.RequestError:
            print("Speech recognition service is unavailable.")
            speak("Speech recognition service is down. Please try again later.")

    return None


def get_transit_details(start_location, end_location):
    """Fetches transit details including bus numbers and stops."""
    try:
        directions = gmaps.directions(start_location, end_location, mode="transit")
        if not directions:
            speak("No transit route found.")
            return None

        steps = directions[0]['legs'][0]['steps']
        transit_steps = []

        for step in steps:
            if "transit_details" in step:
                transit_details = step["transit_details"]
                line_name = transit_details.get("line", {}).get("name", "Unknown Route")
                vehicle_type = transit_details.get("line", {}).get("vehicle", {}).get("type", "Unknown Vehicle")
                bus_number = transit_details.get("line", {}).get("short_name", "No Bus Number")
                departure_stop = transit_details.get("departure_stop", {}).get("name", "Unknown Stop")
                arrival_stop = transit_details.get("arrival_stop", {}).get("name", "Unknown Stop")

                transit_steps.append(
                    f"Take {vehicle_type} {bus_number} from {departure_stop} to {arrival_stop} on route {line_name}."
                )

        return transit_steps
    except googlemaps.exceptions.ApiError as e:
        print(f"Google Maps API Error: {e}")
        return None


def get_directions(start_location, end_location, mode="transit"):
    """Fetches directions for the given travel mode and provides voice navigation."""
    try:
        directions = gmaps.directions(start_location, end_location, mode=mode)

        if not directions:
            speak("No route found. Try another destination.")
            return

        steps = directions[0]['legs'][0]['steps']

        for step in steps:
            instruction = step["html_instructions"]
            instruction = instruction.replace('<b>', '').replace('</b>', '').replace('</div>', '').replace('<div style="font-size:0.9em">', '')
            print(f"Navigation: {instruction}")
            speak(instruction)
    except googlemaps.exceptions.ApiError as e:
        print(f"Google Maps API Error: {e}")
        speak("Error fetching directions. Please try again later.")


# MAIN PROGRAM FLOW
print("Detecting precise location...")
start_location = get_precise_location()

if start_location:
    validated_start = validate_location(start_location)
    if validated_start:
        print(f"Current Precise Location: {validated_start}")

        while True:
            destination = get_voice_command("Please say your destination.")
            if destination:
                validated_end = validate_location(destination)
                if validated_end:
                    travel_mode = get_voice_command("How would you like to travel? Say walking, driving, cycling, or transit.")
                    valid_modes = {"walking": "walking", "driving": "driving", "cycling": "bicycling", "transit": "transit"}

                    if travel_mode in valid_modes:
                        selected_mode = valid_modes[travel_mode]
                    else:
                        speak("Invalid mode selected. Defaulting to transit.")
                        selected_mode = "transit"  # Default to transit

                    print(f"Selected Travel Mode: {selected_mode}")

                    if selected_mode == "transit":
                        transit_info = get_transit_details(validated_start, validated_end)
                        if transit_info:
                            for info in transit_info:
                                print(info)
                                speak(info)
                        else:
                            speak("No transit information available.")
                    else:
                        get_directions(validated_start, validated_end, mode=selected_mode)
                    break
                else:
                    speak("Invalid destination. Trying to find alternatives...")
            else:
                speak("No destination received. Please try again.")
    else:
        speak("Invalid start location.")
else:
    speak("Could not fetch precise location.")
