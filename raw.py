import wave
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, filtfilt
import speech_recognition as sr
from pydub import AudioSegment, effects
import noisereduce as nr
import os

class ShortPhraseTranscriber:
    def __init__(self, wav_file):
        self.wav_file = wav_file

    def optimize_for_speech(self):
        """Optimize audio specifically for short phrase recognition"""
        try:
            print("\nOptimizing audio for speech recognition...")
            
            # Load audio
            audio = AudioSegment.from_wav(self.wav_file)
            
            # Convert to mono and set optimal sample rate
            audio = audio.set_channels(1)
            audio = audio.set_frame_rate(16000)
            
            # Normalize and boost voice frequencies
            audio = effects.normalize(audio)
            audio = audio + 40  # Significant volume boost
            
            # Export base version
            audio.export("temp_base.wav", format="wav")
            
            # Read for additional processing
            rate, data = wavfile.read("temp_base.wav")
            data = data.astype(np.float32)
            
            # Aggressive noise reduction
            clean_data = nr.reduce_noise(
                y=data,
                sr=rate,
                prop_decrease=0.99,
                n_std_thresh_stationary=1.1
            )
            
            # Speech-focused bandpass filter
            nyquist = rate / 2
            cutoffs = [250, 3500]  # Wider range for better clarity
            b, a = butter(4, [f/nyquist for f in cutoffs], btype='band')
            filtered = filtfilt(b, a, clean_data)
            
            # Create three versions with different speeds
            speeds = [1.0, 0.8, 0.5]  # Normal, slightly slow, and slower
            processed_files = []
            
            for speed in speeds:
                # Adjust speed and save
                if speed == 0.5:
                    output_data = filtered
                else:
                    # Resample for speed change
                    new_len = int(len(filtered) / speed)
                    output_data = np.interp(
                        np.linspace(0, len(filtered)-1, new_len),
                        np.arange(len(filtered)),
                        filtered
                    )
                
                # Normalize and convert to int16
                output_data = output_data / np.max(np.abs(output_data))
                output_data = np.int16(output_data * 32767)
                
                # Save version
                output_file = f"processed_speed_{speed}.wav"
                wavfile.write(output_file, rate, output_data)
                processed_files.append(output_file)
            
            print("Audio optimization complete.")
            return processed_files
            
        except Exception as e:
            print(f"Optimization error: {e}")
            return []

    def transcribe(self):
        """Transcribe with multiple attempts"""
        try:
            # Get optimized versions
            processed_files = self.optimize_for_speech()
            if not processed_files:
                return None
            
            recognizer = sr.Recognizer()
            all_results = []
            
            # Recognition settings to try
            configs = [
                (300, 0.8),   # Default
                (200, 1.0),   # More sensitive
                (400, 0.6)    # Less sensitive
            ]
            
            # Try each processed file
            for audio_file in processed_files:
                print(f"\nAttempting recognition on {audio_file}...")
                
                with sr.AudioFile(audio_file) as source:
                    # Try different recognition configurations
                    for energy, pause in configs:
                        recognizer.energy_threshold = energy
                        recognizer.pause_threshold = pause
                        recognizer.dynamic_energy_threshold = True
                        
                        # Get audio data
                        audio = recognizer.record(source)
                        
                        # Try recognition with different language models
                        for language in ['en-US', 'en-GB', 'en-IN']:
                            try:
                                text = recognizer.recognize_google(
                                    audio,
                                    language=language
                                )
                                if text:
                                    all_results.append(text)
                                    print(f"Detected: {text}")
                            except sr.UnknownValueError:
                                continue
                            except sr.RequestError:
                                continue
                        
                        # Reset for next attempt
                        source.stream.seek(0)
            
            # Process results
            if all_results:
                # Get most common result
                from collections import Counter
                most_common = Counter(all_results).most_common(1)[0][0]
                return most_common
            
            return None
            
        except Exception as e:
            print(f"Transcription error: {e}")
            return None
        
        finally:
            # Cleanup
            self.cleanup()

    def cleanup(self):
        """Remove temporary files"""
        temp_files = ["temp_base.wav"] + [f"processed_speed_{speed}.wav" for speed in [1.0, 0.8, 0.6]]
        for file in temp_files:
            if os.path.exists(file):
                try:
                    os.remove(file)
                except:
                    pass

def main():
    wav_file = "Thank you for contac.wav"
    
    print(f"Processing file: {wav_file}")
    transcriber = ShortPhraseTranscriber(wav_file)
    
    result = transcriber.transcribe()
    if result:
        print("\nFinal transcription result:")
        print("-" * 50)
        print(result)
        print("-" * 50)
        
        # Save result
        with open("transcription.txt", "w", encoding='utf-8') as f:
            f.write(result)
        print("\nTranscription saved to 'transcription.txt'")
    else:
        print("\nCould not recognize speech. Suggestions:")
        print("1. Check that the WAV file is not corrupted")
        print("2. Try recording with:")
        print("   - Less background noise")
        print("   - Clearer pronunciation")
        print("   - Slightly slower speech")
        print("3. Ensure microphone is close enough")

if __name__ == "__main__":
    main()