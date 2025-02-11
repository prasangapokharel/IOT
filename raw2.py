import speech_recognition as sr
import pyttsx3
import requests
import json
import os
import wave
import time
import librosa
from dotenv import load_dotenv

# Load environment variables (e.g., API keys)
load_dotenv()

class RobotVoiceSystem:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.setup_voice()
        self.api_key = os.getenv('OPENAI_API_KEY')
        
    def setup_voice(self):
        """Configure voice settings for a more robotic response"""
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if "female" in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break
        self.engine.setProperty('rate', 150)  # Set to 0.75x speed
        self.engine.setProperty('volume', 1)

    def process_audio(self, input_wav):
        """Convert input WAV to text with noise reduction and error handling"""
        try:
            y, sr = librosa.load(input_wav, sr=None)
            librosa.output.write_wav("temp.wav", y, sr)
            with sr.AudioFile("temp.wav") as source:
                self.recognizer.adjust_for_ambient_noise(source)
                print("Processing audio...")
                audio = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio)
                print(f"Transcribed text: {text}")
                return text
        except sr.UnknownValueError:
            print("Could not understand the audio.")
        except sr.RequestError:
            print("Speech recognition service is unavailable.")
        except Exception as e:
            print(f"Audio processing error: {e}")
        return None

    def get_ai_response(self, text):
        """Get AI-generated response with enhanced error handling"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "You are a futuristic robot assistant. Keep responses under 50 words."},
                    {"role": "user", "content": text}
                ]
            }
            response = requests.post(
                'https://openrouter.ai/api/v1/chat/completions',
                headers=headers,
                json=payload
            )
            if response.status_code == 200:
                ai_response = response.json()['choices'][0]['message']['content']
                print(f"AI Response: {ai_response}")
                return ai_response
            else:
                print("Error from API. Using fallback response.")
        except Exception as e:
            print(f"API error: {e}")
        return "I'm sorry, I cannot process your request at the moment."

    def create_audio_response(self, text, output_wav):
        """Convert text to WAV with AI-like speech"""
        try:
            self.engine.save_to_file(text, output_wav)
            self.engine.runAndWait()
            print(f"Audio response saved to {output_wav}")
            return True
        except Exception as e:
            print(f"Speech generation error: {e}")
            return False

    def analyze_wav(self, wav_file):
        """Analyze WAV file properties"""
        try:
            with wave.open(wav_file, 'rb') as audio:
                channels = audio.getnchannels()
                sample_width = audio.getsampwidth()
                frame_rate = audio.getframerate()
                num_frames = audio.getnframes()
                duration = num_frames / frame_rate

                print("\nWAV File Analysis:")
                print(f"- Channels: {'Mono' if channels == 1 else 'Stereo'}")
                print(f"- Sample Rate: {frame_rate} Hz")
                print(f"- Sample Width: {sample_width * 8} bits ({sample_width} bytes)")
                print(f"- Duration: {duration:.2f} seconds")
                print(f"- Total Frames: {num_frames}")
        except Exception as e:
            print(f"Error analyzing WAV file: {e}")

    def run(self, input_wav="AUDIO.wav", output_wav="output.wav"):
        """Main processing function"""
        if not os.path.exists(input_wav):
            print("Input WAV file not found.")
            return
        
        text = self.process_audio(input_wav)
        if not text:
            return
        
        response = self.get_ai_response(text)
        success = self.create_audio_response(response, output_wav)
        
        if success:
            self.analyze_wav(output_wav)
        else:
            print("Failed to generate voice response.")

if __name__ == "__main__":
    robot = RobotVoiceSystem()
    robot.run()
