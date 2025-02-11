from gtts import gTTS
import playsound
import re
import sys
import inflect

class AdvancedTTSConverter:
    def __init__(self):
        """Initialize the enhanced TTS engine with female-like voice settings."""
        self.inflect_engine = inflect.engine()
        self.language = 'en'
        self.slow = False  # Faster, natural speech

    def normalize_numbers(self, text):
        """Convert numbers to words."""
        def replace_number(match):
            number = match.group(0)
            try:
                if '.' in number:  # Decimal numbers
                    return self.inflect_engine.number_to_words(float(number))
                elif len(number) == 4 and number.startswith(('19', '20')):  # Years
                    return number[:2] + ' ' + self.inflect_engine.number_to_words(int(number[2:]))
                else:
                    return self.inflect_engine.number_to_words(int(number))
            except:
                return number

        return re.sub(r'\b\d+\.?\d*\b', replace_number, text)

    def add_speech_patterns(self, text):
        """Add natural speech patterns."""
        text = text.replace(",", "...")
        return text

    def text_to_speech(self, text, output_file='output.wav'):
        """Convert text to speech and save as audio file."""
        try:
            normalized_text = self.normalize_numbers(text)
            processed_text = self.add_speech_patterns(normalized_text)
            print(f"Speaking: {processed_text}")
            tts = gTTS(text=processed_text, lang=self.language, slow=self.slow)
            tts.save(output_file)
            print(f"Audio saved as: {output_file}. Playing audio...")
            playsound.playsound(output_file)
        except Exception as e:
            print(f"Speech generation error: {e}")

if __name__ == '__main__':
    # Read text from prompt.txt
    try:
        with open('prompt.txt', 'r') as file:
            text_to_convert = file.read()
        converter = AdvancedTTSConverter()
        converter.text_to_speech(text_to_convert)
    except FileNotFoundError:
        print("prompt.txt not found. Please provide a valid file.")
