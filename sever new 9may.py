import speech_recognition as sr
import pyttsx3
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import time
import datetime as dt
import requests
import spacy
import googlemaps
import webbrowser
import pyaudio
import socket
import joblib
import numpy as np
import warnings
from spacy.matcher import Matcher
import matplotlib.pyplot as plt
import pyaudio
import socket
import threading

# Load the trained model from the file
classifier = joblib.load('heart_rate_classifier.pkl')
nlp = spacy.load("en_core_web_sm")
warnings.filterwarnings("ignore", category=UserWarning)
accuracy_scores = []
total_attempts = 0
unrecognized_attempts = 0
stored_audio = None
cred = credentials.Certificate(r"") #use the api security key
firebase_admin.initialize_app(cred, {'databaseURL': ''}) #use your database api key
#fetch data (i.e firebase implementation)

def fetch_mq2_sensor_reading():
    ref_path = 'user1/gas'
    mq2_sensor_ref = db.reference(ref_path)
    mq2_sensor_data = mq2_sensor_ref.get()
    return mq2_sensor_data

def check_mq2_sensor_abnormality(reading):
    threshold = 500
    return reading > threshold

def fetch_pulse_sensor_reading():
    ref_path = 'user1/pulse'
    pulse_sensor_ref = db.reference(ref_path)
    pulse_sensor_data = pulse_sensor_ref.get()
    return pulse_sensor_data

def analyze_heart_rate(heart_rate):
    # Convert the scalar value to a numpy array
    pulse_reading_array = np.array([heart_rate])

    # Reshape the pulse_reading into a 2D array with a single feature
    pulse_reading_2d = pulse_reading_array.reshape(-1, 1)
    predictions = classifier.predict(pulse_reading_2d)
    return predictions

def check_pulse_sensor_critical_low(reading):
    return reading < 30

def smoke():
    mq2_sensor_reading = fetch_mq2_sensor_reading()
    mq2_abnormal = check_mq2_sensor_abnormality(mq2_sensor_reading)
    if mq2_abnormal:
        speak("There is a chance of fire near you! please be safe!")
    else:
        speak("You are safe!No possibilities of fire around you!")

def heart():
    pulse_sensor_reading = fetch_pulse_sensor_reading()
    pulse_abnormal = analyze_heart_rate(pulse_sensor_reading)
    if pulse_abnormal[0] == 1:
        speak("Your heart rate is abnormal. Please seek medical attention.")
    else:
        speak("Your pulse rate is normal! nothing to worry!")

def monitor_sensors():
    while True:
        pulse_reading = fetch_pulse_sensor_reading()
        mq2_reading = fetch_mq2_sensor_reading()

        pulse_abnormal = check_pulse_sensor_critical_low(pulse_reading)
        pulse_abnormal2 = analyze_heart_rate(pulse_reading)
        mq2_abnormal = check_mq2_sensor_abnormality(mq2_reading)

        if pulse_abnormal:
            speak("Your pulse rate is critically low or high! Sending alert to nearby devices.")
            alert()
        elif pulse_abnormal2[0] == 1:
            speak("Your heart rate is abnormal. Please seek medical attention.")
        if mq2_abnormal:
            speak("there is possiblity of fire around you! please be careful or ask for help!")

        time.sleep(25)

def send_alert(host, port, message):
    # Create a socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect to the receiver
        client_socket.connect((host, port))

        # Send the message
        client_socket.sendall(message.encode())

        print("Alert message sent successfully.")
    except Exception as e:
        print(f"Error sending alert message: {e}")
    finally:
        # Close the socket
        client_socket.close()

#HOST & PORT INFO
def alert():
    host = '192.168.61.153'  # Receiver's IP address
    port = 12346  # Receiver's port
    message = "Device 1 requires health assistance"  # Alert message to send

    send_alert(host, port, message)

def help():
    audio_data = record_audio()
    port = 12345  # Choose a suitable port number
    send_audio_broadcast(audio_data, port)
    speak("Your location description has been sent to the nearby rescuers! they will assist you soon please be safe until then!")

def mylocation():
    api_key = 'AIzaSyBscHwxlhUcnfN7gt0KizJPPkYVRqRdrcA'
    gmaps = googlemaps.Client(key=api_key)
    user_location = gmaps.geolocate()
    latitude = 12.875746
    longitude = 80.08338

    print("Latitude:", latitude)
    print("Longitude:", longitude)
    return latitude,longitude

def weather(latitude,longitude):
    def kel_to_cel_fah(kelvin):
        celsius = kelvin - 273.15
        fahrenheit = celsius * (9 / 5) + 32
        return celsius

    def kel_to_cel_fah(kelvin):
        celsius = kelvin - 273.15
        fahrenheit = celsius * (9 / 5) + 32
        return celsius

    BASE_URL = "https://api.openweathermap.org/data/2.5/weather?"
    API_KEY = "5ca591b78f132fd9f493c4ba8939377d"
    LATITUDE = latitude
    LONGITUDE = longitude

    url = f"{BASE_URL}lat={LATITUDE}&lon={LONGITUDE}&appid={API_KEY}"

    response = requests.get(url).json()

    print(response)

    temp_kelvin = response['main']['temp']
    temp_celsius = kel_to_cel_fah(temp_kelvin)
    feels_like_kelvin = response['main']['feels_like']
    feels_like_celsius = kel_to_cel_fah(feels_like_kelvin)
    Wind_speed = response['wind']['speed']
    humidity = response['main']['humidity']
    description = response['weather'][0]['description']

    print(f"Temperature in your location: {temp_celsius:.2f} C")
    print(f"Temperature in your location: feels like {feels_like_celsius:.2f} C")
    print(f"Humidity in your location: {humidity}%")
    print(f"Wind speed in your location: {Wind_speed}M/S")
    print(f"General weather in your location: {description}")

    speak(f"Temperature in your location: {temp_celsius:.2f} degree Celsius")
    speak(f"Temperature in your location: feels like {feels_like_celsius:.2f} degree Celsius")
    speak(f"Humidity in your location: {humidity}%")
    speak(f"Wind speed in your location: {Wind_speed}meter per second")
    speak(f"General weather in your location: {description}")

    speak("Thank you ! have a nice day!")

def map(latitude,longitude):
    def webmap(api_key):
        map_url = f"https://www.google.com/maps/place/{latitude},{longitude}"
        webbrowser.open(map_url)
    webmap("AIzaSyBscHwxlhUcnfN7gt0KizJPPkYVRqRdrcA")
#this navigation will be done when we recieve a location from other device

def route_map(end_latitude,end_longitude):
    def fetch_my_location(api_key):
        gmaps = googlemaps.Client(key=api_key)
        user_location = gmaps.geolocate()
        return user_location['location']['lat'], user_location['location']['lng']

    def navigate_to_location_with_route(api_key, end_latitude, end_longitude):
        start_latitude, start_longitude = fetch_my_location(api_key)
        map_url = f"https://www.google.com/maps/dir/{start_latitude},{start_longitude}/{end_latitude},{end_longitude}"
        webbrowser.open(map_url)

    api_key = 'AIzaSyBscHwxlhUcnfN7gt0KizJPPkYVRqRdrcA'

    navigate_to_location_with_route(api_key, end_latitude, end_longitude)

def record_audio():
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100

    audio = pyaudio.PyAudio()

    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    print("Recording...")
    frames = []

    for _ in range(0, int(RATE / CHUNK * 10)):  # Record for 10 seconds
        data = stream.read(CHUNK)
        frames.append(data)

    print("Finished recording.")

    stream.stop_stream()
    stream.close()
    audio.terminate()

    return b''.join(frames)

def send_audio_broadcast(audio_data, port):
    CHUNK_SIZE = 1024  # Adjust chunk size as needed
    END_MARKER = b'_END_'

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Split audio data into chunks and send them sequentially
    for i in range(0, len(audio_data), CHUNK_SIZE):
        chunk = audio_data[i:i + CHUNK_SIZE]
        sock.sendto(chunk, ('<broadcast>', port))

    # Send end marker to indicate the end of transmission
    sock.sendto(END_MARKER, ('<broadcast>', port))

    sock.close()
    print("audio sent")

def near_me():
    nearby_devices=1
    speak(f"nearby devices:{nearby_devices}")

def speak(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    engine.say(text)
    engine.runAndWait()

def process_input(text):
    doc = analyze_text(text)
    # Handle recognized intents
    if doc is not None:
        if all(token.text.lower() in ["hello", "voice", "assistant"] for token in doc):
            speak("Hello! How can I assist you?")
        elif any(token.text.lower() in ["stop", "over","terminate","bye"] for token in doc):
            speak("Stopping.")
            generate_report()
            exit()  # Exiting the program gracefully
        elif all(token.text.lower() in ["how", "are", "you"] for token in doc):
            speak("I'm doing well, thank you!")
        elif all(word in [token.text.lower() for token in doc] for word in ["what", "can", "you", "do"]):
            speak("I am your personal assistant! You can ask me about your pulse, abnormalities around you, about the weather in your location, and about the details of other rescuers.")
        elif any(token.text.lower() == "pulse" for token in doc):
            heart()
        elif any(token.text.lower() == "smoke" for token in doc):
            smoke()
        elif all(word in [token.text.lower() for token in doc] for word in ["my", "location"]) or all(word in [token.text.lower() for token in doc] for word in ["where", "am", "i"]):
            latitude, longitude = mylocation()
            speak(f"Your coordinates are latitude {latitude} and longitude {longitude}.")
            speak("Do you want to view your location on Google Maps?")
        elif any(word in [token.text.lower() for token in doc] for word in ["yes","i want to"]):
            latitude, longitude = mylocation()
            map(latitude,longitude)
        elif any(word in [token.text.lower() for token in doc] for word in ["weather", "climate"]):
            latitude, longitude = mylocation()
            speak("Here is the weather report for your location.")
            weather(latitude, longitude)
        elif all(word in [token.text.lower() for token in doc] for word in ["near", "me", "other", "rescuers"]):
            speak("Searching for nearby rescuers...")
            near_me()
        elif all(word in [token.text.lower() for token in doc] for word in ["send", "me", "help"]):
            speak("Please describe the place you are at right now!")
            help()
            return
        elif any(word in [token.text.lower() for token in doc] for word in ["give", "overall", "condition", "status"]):
            speak("Analyzing overall condition...")
            latitude, longitude = mylocation()
            weather(latitude, longitude)
            heart()
            smoke()
            near_me()
            return
        else:
            speak("Sorry, I didn't understand that. Can you please repeat?")
    else:
        speak("Sorry, I didn't understand that. Can you please repeat?")

stored_audio = None

def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)

    try:
        recognized_text = recognizer.recognize_google(audio)
        global stored_audio  # Access the stored_audio variable
        stored_audio = audio  # Store the captured audio
        return recognized_text.lower(),stored_audio  # Return recognized text
    except sr.UnknownValueError:
        print("Could not understand audio.")
        return None,None
    except sr.RequestError as e:
        print(f"Error accessing Google Speech Recognition service: {e}")
        return None,None

def analyze_text(text):
    doc = nlp(text)
    return doc

def calculate_accuracy(recognized_text, stored_audio):
    if stored_audio is not None:
        recognizer = sr.Recognizer()
        try:
            actual_text = recognizer.recognize_google(audio_data=stored_audio)
            total_words = len(actual_text.split())
            correct_words = sum(1 for word in actual_text.split() if word in recognized_text.split())
            accuracy_percentage = (correct_words / total_words) * 100
            return accuracy_percentage
        except sr.UnknownValueError:
            print("Could not understand stored audio.")
        except sr.RequestError as e:
            print(f"Error accessing Google Speech Recognition service for stored audio: {e}")
    return None

def generate_report():
    print("Accuracy Scores:")
    for idx, accuracy in enumerate(accuracy_scores, 1):
        print(f"Speech {idx}: {accuracy}")
    overall_accuracy = sum(accuracy_scores) / total_attempts if total_attempts != 0 else 0
    unrecognized_percentage = (unrecognized_attempts / total_attempts) * 100 if total_attempts != 0 else 0
    print("Percentage of Unrecognized Audio:", unrecognized_percentage)
    print("Overall Accuracy:", overall_accuracy)
    print("Percentage of Unrecognized Audio:", unrecognized_percentage)

    # Plot accuracy scores over time
    plt.plot(range(1, len(accuracy_scores) + 1), accuracy_scores, marker='o')
    plt.title('Accuracy Over Time')
    plt.xlabel('Speech')
    plt.ylabel('Accuracy')
    plt.grid(True)
    plt.show()

def recognise():
    stored_audio = None
    global total_attempts, unrecognized_attempts
    while True:
        start_time = time.time()  # Record the start time
        recognized_text,stored_audio = recognize_speech()  # Recognize speech and get audio data
        if recognized_text is not None:
            print("Recognized:", recognized_text)
            end_time = time.time()  # Record the end time
            response_time = end_time - start_time  # Calculate the response time
            print("Response time:",response_time,"Sec")
            process_input(recognized_text)
            accuracy = calculate_accuracy(recognized_text, stored_audio)  # Pass stored audio for comparison
            if stored_audio is None:
                unrecognized_attempts += 1
                return unrecognized_attempts
            if accuracy is not None:
                accuracy_scores.append(accuracy)
                print("Accuracy:", accuracy)
            else:
                unrecognized_attempts += 1
        total_attempts +=1

def main():
    speak("Hello! I am your assistant in this rescue mission! please ask if you need help or any details about your surroundings and yourself!")
    stored_audio = None
    global total_attempts, unrecognized_attempts
    recognition_thread = threading.Thread(target=recognise)
    sensor_monitoring_thread = threading.Thread(target=monitor_sensors)
    recognition_thread.start()
    sensor_monitoring_thread.start()

    # Wait for threads to finish (which they won't, as they're infinite loops)
    recognition_thread.join()
    sensor_monitoring_thread.join()

main()
