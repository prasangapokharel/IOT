import pyttsx3
import time
from pathlib import Path
import sys
import re
from num2words import num2words
import inflect

class AdvancedTTSConverter:
    def __init__(self):
        """Initialize the enhanced TTS engine with Siri-like voice settings."""
        try:
            self.engine = pyttsx3.init()
            self.inflect_engine = inflect.engine()
            self.configure_voice()
            self.configure_speech_properties()
            
        except Exception as e:
            print(f"Initialization error: {e}")
            sys.exit(1)

    def configure_voice(self):
        """Configure voice settings for Siri-like natural speech."""
        voices = self.engine.getProperty('voices')
        
        # Priority voice characteristics for Siri-like sound
        premium_voices = {
            'windows': ['IVONA', 'Cortana', 'Microsoft Zira'],
            'darwin': ['Samantha', 'Victoria'],  # macOS voices
            'linux': ['espeak-ng-mbrola-us1', 'espeak-ng-mbrola-us2']
        }
        
        selected_voice = None
        current_platform = sys.platform
        
        # First try to find premium voices for the current platform
        platform_voices = premium_voices.get('windows' if current_platform.startswith('win') else
                                           'darwin' if current_platform.startswith('darwin') else
                                           'linux')
        
        if platform_voices:
            for voice in voices:
                if any(premium in voice.name for premium in platform_voices):
                    selected_voice = voice
                    break
        
        # Fallback to any female voice if premium not found
        if not selected_voice:
            for voice in voices:
                if 'female' in voice.name.lower():
                    selected_voice = voice
                    break
        
        if selected_voice:
            self.engine.setProperty('voice', selected_voice.id)
            print(f"Using premium voice: {selected_voice.name}")
        else:
            print("No suitable voice found. Please install additional voice packages.")
            sys.exit(1)

    def configure_speech_properties(self):
        """Configure advanced speech properties for natural sound."""
        # Set optimal speech rate (slightly faster than default for Siri-like pace)
        self.engine.setProperty('rate', 175)  # Adjusted for more natural pacing
        
        # Set volume with slight reduction for clearer audio
        self.engine.setProperty('volume', 0.85)  # 85% volume for better clarity

    def normalize_numbers(self, text):
        """Convert numbers to words with natural speech patterns."""
        def replace_number(match):
            number = match.group(0)
            try:
                # Handle special cases
                if '.' in number:  # Decimal numbers
                    return self.inflect_engine.number_to_words(float(number))
                elif len(number) == 4 and number.startswith(('19', '20')):  # Years
                    return number[:2] + ' ' + self.inflect_engine.number_to_words(int(number[2:]))
                else:
                    return self.inflect_engine.number_to_words(int(number))
            except:
                return number
        
        # Find numbers in text and convert them
        return re.sub(r'\b\d+\.?\d*\b', replace_number, text)

    def add_speech_patterns(self, text):
        """Add natural speech patterns and inflections without NLTK dependency."""
        # Split text into sentences using simple regex
        sentences = re.split(r'(?<=[.!?])\s+', text)
        processed_sentences = []
        
        for sentence in sentences:
            # Add subtle pauses for natural rhythm
            sentence = re.sub(r'([.!?,:;])', r'\1 ', sentence)
            
            # Add emphasis on important words
            sentence = re.sub(r'\b(must|never|always|critical|important)\b',
                            r'\1', 
                            sentence, 
                            flags=re.IGNORECASE)
            
            # Add natural pauses
            sentence = sentence.strip() + " ... "
            processed_sentences.append(sentence)
        
        return ' '.join(processed_sentences)

    def preprocess_text(self, text):
        """Enhanced text preprocessing for natural speech."""
        # Convert common abbreviations
        abbreviations = {
            'Dr.': 'Doctor',
            'Mr.': 'Mister',
            'Mrs.': 'Misses',
            'Ms.': 'Miss',
            'Prof.': 'Professor',
            'Sr.': 'Senior',
            'Jr.': 'Junior',
            'vs.': 'versus',
            'etc.': 'etcetera',
            'approx.': 'approximately',
            'temp.': 'temperature',
        }
        
        for abbr, full in abbreviations.items():
            text = text.replace(abbr, full)
        
        # Convert numbers to words
        text = self.normalize_numbers(text)
        
        # Add natural speech patterns
        text = self.add_speech_patterns(text)
        
        # Handle special characters for better pronunciation
        text = text.replace('-', ' ')
        text = text.replace('&', ' and ')
        
        return text

    def convert_to_speech(self, input_path, output_path):
        """Convert text to speech with enhanced natural processing."""
        try:
            input_path = Path(input_path)
            if not input_path.exists():
                raise FileNotFoundError(f"Input file not found: {input_path}")

            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            print("Starting conversion with natural voice enhancement...")
            
            # Read and process text
            with open(input_path, 'r', encoding='utf-8') as file:
                text = file.read()

            # Apply enhanced preprocessing
            processed_text = self.preprocess_text(text)
            
            print("Applying voice naturalization...")
            self.engine.save_to_file(processed_text, str(output_path))
            self.engine.runAndWait()

            if output_path.exists():
                print("✓ Voice conversion completed successfully")
                print(f"✓ Output saved to: {output_path}")
                print(f"✓ Audio size: {output_path.stat().st_size / 1024:.2f} KB")
            else:
                raise Exception("Failed to generate audio file")

        except Exception as e:
            print(f"Error during conversion: {e}")
            sys.exit(1)

def main():
    """Main function with enhanced error handling."""
    try:
        print("Initializing Advanced TTS Converter...")
        converter = AdvancedTTSConverter()
        
        input_file = 'prompt.txt'
        output_file = 'natural_voice_output.wav'
        
        print("Starting voice conversion process...")
        converter.convert_to_speech(input_file, output_file)
        
    except KeyboardInterrupt:
        print("\nConversion cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
    