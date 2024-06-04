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
classifier = joblib.load('PATH OF THE HEARTRATE CLASSIFIER')
nlp = spacy.load("en_core_web_sm")
nearby_devices = {}
warnings.filterwarnings("ignore", category=UserWarning)
accuracy_scores = []
total_attempts = 0
unrecognized_attempts = 0
stored_audio = None
cred = credentials.Certificate("JSON FILE PATH")
firebase_admin.initialize_app(cred, {'databaseURL': 'URL OF THE DATA BASE'})

def fetch_mq2_sensor_reading():
    ref_path = 'PATH OF ATTRIBUTES'
    mq2_sensor_ref = db.reference(ref_path)
    mq2_sensor_data = mq2_sensor_ref.get()
    return mq2_sensor_data

def check_mq2_sensor_abnormality(reading):
    threshold = 500
    return reading > threshold

def fetch_pulse_sensor_reading():
    ref_path = 'PATH OF ATTRIBUTES'
    pulse_sensor_ref = db.reference(ref_path)
    pulse_sensor_data = pulse_sensor_ref.get()
    return pulse_sensor_data

def analyze_heart_rate(heart_rate):
    # Convert the scalar value to a numpy array
    pulse_reading_array = np.array([heart_rate])

    # Reshape the pulse_reading into a 2D array with a single feature
    pulse_reading_2d = pulse_reading_array.reshape(-1, 1)
    predictions = classifier.predict(pulse_reading_2d)
    if predictions[0] == 0 :
        speak("Your heart rate is normal.")
    else:
        speak("Your heart rate is abnormal. Please seek medical attention.")

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
    if pulse_abnormal:
        speak("Your pulse rate is abnormal! please take rest! or ask for help!")
    else:
        speak("Your pulse rate is normal! nothing to worry!")

def monitor_sensors():
    while True:
        pulse_reading = fetch_pulse_sensor_reading()
        mq2_reading = fetch_mq2_sensor_reading()

        pulse_abnormal = check_pulse_sensor_critical_low(pulse_reading)
        pulse_abnormal2 = analyze_heart_rate(pulse_reading)
        mq2_abnormal = check_mq2_sensor_abnormality(mq2_reading)

        if pulse_abnormal or pulse_abnormal2:
            speak("Your pulse rate is critically low or high! Sending alert to nearby devices.")

        if mq2_abnormal:
            speak("there is possiblity of fire around you! please be careful or ask for help!")

        time.sleep(60)

def mylocation():
    api_key = 'GGOGLE MAPS API KEY'
    gmaps = googlemaps.Client(key=api_key)
    user_location = gmaps.geolocate()
    latitude = user_location['location']['lat']
    longitude = user_location['location']['lng']

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
    API_KEY = "OPENWEATHERAPPS API KEY"
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
    sunrise_time = dt.datetime.fromtimestamp(response['sys']['sunrise'] + response['timezone'])
    sunset_time = dt.datetime.fromtimestamp(response['sys']['sunset'] + response['timezone'])

    print(f"Temperature in your location: {temp_celsius:.2f} C")
    print(f"Temperature in your location: feels like {feels_like_celsius:.2f} C")
    print(f"Humidity in your location: {humidity}%")
    print(f"Wind speed in your location: {Wind_speed}M/S")
    print(f"General weather in your location: {description}")
    print(f"sunrise in your location: {sunrise_time} local time")
    print(f"sunset in your location: {sunset_time} local time")

    speak(f"Temperature in your location: {temp_celsius:.2f} degree Celsius")
    speak(f"Temperature in your location: feels like {feels_like_celsius:.2f} degree Celsius")
    speak(f"Humidity in your location: {humidity}%")
    speak(f"Wind speed in your location: {Wind_speed}meter per second")
    speak(f"General weather in your location: {description}")
    speak(f"sunrise in your location: {sunrise_time} local time")
    speak(f"sunset in your location: {sunset_time} local time")

    speak("Thank you ! have a nice day!")

def map(latitude,longitude):
    def webmap(api_key):
        map_url = f"https://www.google.com/maps/place/{latitude},{longitude}"
        webbrowser.open(map_url)
    webmap("GOOGLE MAPS API KEY")

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

    api_key = 'GOOGLE MAPS API KEY'

    navigate_to_location_with_route(api_key, end_latitude, end_longitude)

def record_audio(duration=5, chunk_size=1024, format=pyaudio.paInt16, channels=1, rate=44100):
    """Record audio from the default audio input device for a specified duration."""
    speak("describe about your surroundings! we are sending this audio to the nearby rescuers!")
    audio_recorder = pyaudio.PyAudio()

    stream = audio_recorder.open(format=format,
                                 channels=channels,
                                 rate=rate,
                                 input=True,
                                 frames_per_buffer=chunk_size)

    print("Recording audio...")

    frames = []
    for _ in range(0, int(rate / chunk_size * duration)):
        data = stream.read(chunk_size)
        frames.append(data)

    print("Finished recording.")

    stream.stop_stream()
    stream.close()
    audio_recorder.terminate()

    return b''.join(frames)

def send_audio(audio_data, host, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    client_socket.sendall(audio_data)
    client_socket.close()

def help():
    audio_data = record_audio()
    host = 'RECEIVER API'  # Replace with the IP address of the receiver device (Device B)
    port = 12345  # Specify the port to connect to on the receiver device
    send_audio(audio_data, host, port)
    speak("Your location description has been sent to the nearby rescuers! they will assist you soon please be safe until then!")

def play_audio(audio_data):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100

    audio = pyaudio.PyAudio()

    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, output=True)

    print("Playing audio...")

    # Play audio in chunks
    for i in range(0, len(audio_data), CHUNK):
        stream.write(audio_data[i:i + CHUNK])

    print("Finished playing audio.")

    stream.stop_stream()
    stream.close()
    audio.terminate()

def receive_audio(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', port))

    print("Listening for audio...")

    audio_data = b''
    while True:
        data, addr = sock.recvfrom(4096)  # Adjust buffer size as needed
        if data == b'_END_':
            break
        audio_data += data

    print("Received audio.")
    play_audio(audio_data)
    sock.close()

def receivead():
    port = 12345  # Choose the same port number used in the sender code
    receive_audio(port)

def speak(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    engine.say(text)
    engine.runAndWait()


def get_alert():
    host = '0.0.0.0'  # Listen on all available interfaces
    port = 12346  # Port to listen on

    receive_alert(host, port)

def receive_alert(host, port):
    # Create a socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Bind the socket to the host and port
        server_socket.bind((host, port))

        # Listen for incoming connections
        server_socket.listen(1)

        print("Waiting for connection...")
        while True:
            # Accept a client connection
            client_socket, addr = server_socket.accept()
            print(f"Connection from {addr} established.")

            # Receive the alert message
            alert_message = client_socket.recv(1024).decode()
            print("Received alert message:", alert_message)
            speak("Received alert message:", alert_message)

            # Close the client socket
            client_socket.close()
            print("Connection closed.")
            break  # Only accept one connection and message
    except Exception as e:
        print(f"Error receiving alert message: {e}")
    finally:
        # Close the server socket
        server_socket.close()


def process_input(text):
    doc = analyze_text(text)
    # Handle recognized intents
    if doc is not None:
        if all(token.text.lower() in ["hello", "voice", "assistant"] for token in doc):
            speak("Hello! How can I assist you?")
        elif any(token.text.lower() in ["stop", "over","terminate"] for token in doc):
            speak("Stopping.")
            generate_report()
            exit()  # Exiting the program gracefully
        elif all(token.text.lower() in ["how", "are", "you"] for token in doc):
            speak("I'm doing well, thank you!")
        elif all(word in [token.text.lower() for token in doc] for word in ["what", "can", "you", "do"]):
            speak("I am your personal assistant! You can ask me about your pulse, abnormalities around you, about the weather in your location, and about the details of other rescuers.")
        elif any(token.text.lower() == "pulse" for token in doc):
            #heart()
            pulse_sensor_reading = fetch_pulse_sensor_reading()
            analyze_heart_rate(pulse_sensor_reading)
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
        elif all(word in [token.text.lower() for token in doc] for word in ["status", "of", "other", "rescuers"]):
            speak("Checking status of other rescuers...")
            # Call status function
        elif any(word in [token.text.lower() for token in doc] for word in ["near", "me", "other", "rescuers"]):
            speak("Searching for nearby rescuers...")
            near_me()
        elif any(word in [token.text.lower() for token in doc] for word in ["help"]):
            speak("Please describe the place you are at right now!")
            client_audio(username="harini")
        elif all(word in [token.text.lower() for token in doc] for word in ["overall", "condition"]):
            speak("Analyzing overall condition...")
            latitude, longitude = mylocation()
            weather(latitude, longitude)
            heart()
            smoke()
            near_me()
            # Call status
        else:
            speak("Sorry, I didn't understand that. Can you please repeat?")
    else:
        speak("Sorry, I didn't understand that. Can you please repeat?")
def main():
    audio_thread = threading.Thread(target=receivead)
    alert_thread = threading.Thread(target=get_alert)
    audio_thread.start()
    alert_thread.start()

    # Wait for threads to finish (which they won't, as they're infinite loops)
    audio_thread.join()
    alert_thread.join()

main()