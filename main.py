import speech_recognition as sr
import pyttsx3
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get OpenRouter API keys from the .env file
open_router_keys = [
    os.getenv('OPENAI_API_KEY'),
    os.getenv('OPENAI_API_KEY_2')
]

# Function to convert .wav file to text
def convert_wav_to_text(wav_filename):
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(wav_filename) as source:
            print(f"Processing file: {wav_filename}")
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
            print("Transcription:")
            print(text)
            text_filename = wav_filename.replace('.wav', 'prompt.txt')
            with open(text_filename, 'w') as text_file:
                text_file.write(text)
            print(f"Transcription saved as {text_filename}")
            return text_filename
    except Exception as e:
        print(f"Error processing the audio file: {e}")
        return None

# Function to send transcription to OpenRouter API (GPT-3.5 Turbo)
def read_text_and_send_to_openrouter(text_filename):
    try:
        with open(text_filename, 'r') as file:
            text = file.read()
            print(f"Sending transcription to OpenRouter API...")

            # Choose an API key from the list
            api_key = open_router_keys[0]  # You can rotate keys as needed
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            # Prepare the data payload for the API request
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": text}]
            }

            # Send request to OpenRouter API
            response = requests.post('https://openrouter.ai/api/v1/chat/completions', headers=headers, json=payload)

            # Check the response from the API
            if response.status_code == 200:
                data = response.json()
                gemini_text = data['choices'][0]['message']['content'] if 'choices' in data else "No response from OpenRouter."
                print("OpenRouter Response:")
                print(gemini_text)

                # Save the OpenRouter response to a file
                gemini_text_filename = text_filename.replace('prompt.txt', '_openrouter_response.txt')
                with open(gemini_text_filename, 'w') as text_file:
                    text_file.write(gemini_text)
                print(f"OpenRouter response saved as {gemini_text_filename}")
                return gemini_text, gemini_text_filename
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return None, None
    except Exception as e:
        print(f"Error processing OpenRouter API or reading file: {e}")
        return None, None

# Function to convert text to speech (OpenRouter response)
def text_to_speech(text, output_filename):
    try:
        print("Converting OpenRouter response to audio...")
        engine = pyttsx3.init()

        # Set properties for pyttsx3 engine if needed
        engine.setProperty('rate', 150)  # Speed of speech
        engine.setProperty('volume', 1)  # Volume (0.0 to 1.0)

        # Save the speech output to a file
        engine.save_to_file(text, output_filename)
        engine.runAndWait()
        print(f"Audio saved as {output_filename}")
    except Exception as e:
        print(f"Error during text-to-speech conversion: {e}")

# Function to convert the response .txt file to .wav audio file
def convert_response_txt_to_wav(gemini_text_filename):
    try:
        with open(gemini_text_filename, 'r') as file:
            gemini_text = file.read()
            audio_filename = gemini_text_filename.replace('_openrouter_response.txt', '_result.wav')
            text_to_speech(gemini_text, audio_filename)
            print(f"Converted response to audio: {audio_filename}")
    except Exception as e:
        print(f"Error converting response .txt to .wav: {e}")

# Main function to handle the workflow
def main():
    wav_filename = "Thank you for contac.wav"  # Replace with your .wav file path
    text_filename = convert_wav_to_text(wav_filename)
    if text_filename:
        gemini_text, gemini_text_filename = read_text_and_send_to_openrouter(text_filename)
        if gemini_text:
            # Convert the response .txt file to .wav audio file
            convert_response_txt_to_wav(gemini_text_filename)

if __name__ == "__main__":
    main()
