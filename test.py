from gtts import gTTS
import os
import playsound

class FemaleVoiceTTS:
    def __init__(self, language='en', slow=False):
        """Initialize the TTS system with language and speed."""
        self.language = language
        self.slow = slow  # Set to True if you want a slower speech rate

    def create_audio(self, text, output_file='output.wav'):
        """Convert text to speech and save as WAV file."""
        try:
            tts = gTTS(text=text, lang=self.language, slow=self.slow)
            tts.save(output_file)
            print(f"Audio saved to {output_file}. Playing audio...")
            playsound.playsound(output_file)
        except Exception as e:
            print(f"Error generating audio: {e}")

if __name__ == "__main__":
    tts_system = FemaleVoiceTTS(language='en')  # 'en' for English (US female-like voice)
    text_to_convert = "Hello! Ishan you are my creator."
    
    tts_system.create_audio(text_to_convert)
