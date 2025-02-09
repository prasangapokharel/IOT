import speech_recognition as sr
import pyttsx3
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

class RobotVoiceSystem:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.setup_voice()
        self.api_key = os.getenv('OPENAI_API_KEY')
        
    def setup_voice(self):
        """Configure voice settings for robot-like response"""
        voices = self.engine.getProperty('voices')
        # Select female voice if available
        for voice in voices:
            if "female" in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break
        self.engine.setProperty('rate', 150)    # Moderate speed
        self.engine.setProperty('volume', 0.9)  # Clear volume

    def process_audio(self, input_wav):
        """Convert input WAV to text"""
        try:
            with sr.AudioFile(input_wav) as source:
                print("Processing audio...")
                audio = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio)
                return text
        except Exception as e:
            print(f"Audio processing error: {e}")
            return None

    def get_ai_response(self, text):
        """Get concise AI response"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Prompt engineering for concise responses
            prompt = f"As a robot assistant, provide a clear and concise response (max 50 words) to: {text}"
            
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "You are a helpful robot assistant. Keep responses under 50 words."},
                    {"role": "user", "content": prompt}
                ]
            }

            response = requests.post(
                'https://openrouter.ai/api/v1/chat/completions',
                headers=headers,
                json=payload
            )

            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            return "I apologize, I cannot process your request at the moment."
            
        except Exception as e:
            print(f"API error: {e}")
            return "System processing error occurred."

    def create_audio_response(self, text, output_wav):
        """Convert text to WAV audio"""
        try:
            self.engine.save_to_file(text, output_wav)
            self.engine.runAndWait()
            return True
        except Exception as e:
            print(f"Speech generation error: {e}")
            return False

def main():
    robot = RobotVoiceSystem()
    
    # Process flow
    input_wav = "natural_voice_output.wav"
    output_wav = "robot_response.wav"
    
    # 1. Convert input WAV to text
    text = robot.process_audio(input_wav)
    if not text:
        return
    
    # 2. Get AI response
    response = robot.get_ai_response(text)
    
    # 3. Create audio response
    success = robot.create_audio_response(response, output_wav)
    
    if success:
        print(f"Response saved to {output_wav}")
    else:
        print("Failed to create response")

if __name__ == "__main__":
    main()