import speech_recognition as sr
import pyttsx3
import requests
import json
import os
import wave
import pyaudio  # For playing the audio
from dotenv import load_dotenv

load_dotenv()

class RobotVoiceSystem:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.setup_voice()
        self.api_key = os.getenv('OPENAI_API_KEY')

    def setup_voice(self):
        """Configure voice settings for robot-like response using a female voice"""
        voices = self.engine.getProperty('voices')
        # Select female voice if available
        female_voice_found = False
        for voice in voices:
            if "female" in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                female_voice_found = True
                break
        if not female_voice_found:
            print("Female voice not found. Using default voice.")
        self.engine.setProperty('rate', 150)  # Moderate speed
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
        """Convert text to WAV audio with specified properties (11000 Hz, 8-bit, Mono)"""
        try:
            # Save the speech to a temporary file first
            temp_wav = "temp_output.wav"
            self.engine.save_to_file(text, temp_wav)
            self.engine.runAndWait()

            # Convert the temporary file to the desired properties: 11000 Hz, 8-bit, Mono
            with wave.open(temp_wav, 'rb') as temp_audio:
                # Get the parameters of the temporary file
                params = temp_audio.getparams()

                # Set desired properties for the output WAV file
                new_params = (
                    1,  # Mono channel
                    1,  # 8-bit sample width
                    11000,  # Sample rate: 11000 Hz
                    params.nframes,  # Number of frames (unchanged)
                    params.comptype,  # Compression type
                    params.compname  # Compression name
                )

                # Open the output file with the desired parameters
                with wave.open(output_wav, 'wb') as output_audio:
                    output_audio.setparams(new_params)

                    # Read the original audio data and write it to the new file with adjusted properties
                    frames = temp_audio.readframes(params.nframes)
                    output_audio.writeframes(frames)

            os.remove(temp_wav)  # Clean up the temporary file
            return True
        except Exception as e:
            print(f"Speech generation error: {e}")
            return False

    def play_wav(self, wav_file):
        """Play the WAV file with the specified sample rate, width, and channels"""
        try:
            wf = wave.open(wav_file, 'rb')
            p = pyaudio.PyAudio()

            stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                            channels=wf.getnchannels(),
                            rate=wf.getframerate(),
                            output=True)

            data = wf.readframes(1024)

            while data:
                stream.write(data)
                data = wf.readframes(1024)

            stream.stop_stream()
            stream.close()
            p.terminate()
        except Exception as e:
            print(f"Error playing WAV file: {e}")

    def analyze_wav(self, wav_file):
        """Analyze and display WAV file properties"""
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

def main():
    robot = RobotVoiceSystem()
    
    # Process flow
    input_wav = "AUDIO (3).wav"  # Input WAV file (ensure it's valid)
    output_wav = "output.wav"  # Output WAV file with desired properties (11000 Hz, 8-bit, Mono)
    
    # 1. Convert input WAV to text
    text = robot.process_audio(input_wav)
    if not text:
        return
    
    print(f"User said: {text}")
    
    # 2. Get AI response
    response = robot.get_ai_response(text)
    
    print(f"AI Response: {response}")
    
    # 3. Create audio response with the desired properties
    success = robot.create_audio_response(response, output_wav)
    
    if success:
        print(f"Response saved to {output_wav}")
        
        # Analyze and print properties of the output WAV file
        robot.analyze_wav(output_wav)
        
        # 4. Play the processed output WAV file
        robot.play_wav(output_wav)
    else:
        print("Failed to create response")

if __name__ == "__main__":
    main()
