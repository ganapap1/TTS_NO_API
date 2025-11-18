"""
Piper TTS Test Script
Tests Piper TTS quality before full integration.
Run: python test_piper.py
"""

import subprocess
import sys
import os
from pathlib import Path

def install_piper():
    """Install piper-tts if not already installed."""
    print("Checking piper-tts installation...")
    try:
        import piper
        print("piper-tts is already installed.")
        return True
    except ImportError:
        print("Installing piper-tts...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "piper-tts"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("piper-tts installed successfully!")
            return True
        else:
            print(f"Installation failed: {result.stderr}")
            return False

def download_voice(voice_name="en_US-amy-medium"):
    """Download a Piper voice model."""
    models_dir = Path("models/piper")
    models_dir.mkdir(parents=True, exist_ok=True)

    model_path = models_dir / f"{voice_name}.onnx"
    config_path = models_dir / f"{voice_name}.onnx.json"

    if model_path.exists() and config_path.exists():
        print(f"Voice '{voice_name}' already downloaded.")
        return str(model_path)

    print(f"Downloading voice: {voice_name}...")

    # Piper voice URLs from Hugging Face
    base_url = f"https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium"
    model_url = f"{base_url}/en_US-amy-medium.onnx"
    config_url = f"{base_url}/en_US-amy-medium.onnx.json"

    try:
        import urllib.request

        # Download model file
        print(f"Downloading model file (~50MB)...")
        urllib.request.urlretrieve(model_url, model_path, reporthook=download_progress)
        print()  # New line after progress

        # Download config file
        print("Downloading config file...")
        urllib.request.urlretrieve(config_url, config_path)

        print(f"Voice downloaded to: {model_path}")
        return str(model_path)

    except Exception as e:
        print(f"Download failed: {e}")
        return None

def download_progress(block_num, block_size, total_size):
    """Show download progress."""
    downloaded = block_num * block_size
    percent = min(100, (downloaded / total_size) * 100)
    bar_length = 40
    filled = int(bar_length * percent / 100)
    bar = '=' * filled + '-' * (bar_length - filled)
    print(f"\r[{bar}] {percent:.1f}%", end='', flush=True)

def generate_test_audio(model_path):
    """Generate test audio using Piper."""
    print("\nGenerating test audio...")

    try:
        from piper import PiperVoice
        import wave
        import struct

        # Load the voice model
        print("Loading voice model...")
        voice = PiperVoice.load(model_path)

        # Test texts
        test_texts = [
            "Hello! This is a test of Piper text to speech running completely offline on your computer.",
            "The quick brown fox jumps over the lazy dog. This sentence contains every letter of the alphabet.",
            "Piper uses neural networks to generate natural sounding speech without requiring an internet connection or GPU."
        ]

        output_dir = Path("test_output")
        output_dir.mkdir(exist_ok=True)

        for i, text in enumerate(test_texts, 1):
            output_path = output_dir / f"piper_test_{i}.wav"

            print(f"Generating sample {i}/3...")

            # Generate audio using synthesize method
            with wave.open(str(output_path), 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(voice.config.sample_rate)

                # Synthesize returns AudioChunk objects with audio_int16_bytes
                for audio_chunk in voice.synthesize(text):
                    wav_file.writeframes(audio_chunk.audio_int16_bytes)

            print(f"  Saved: {output_path}")

        print("\n" + "="*50)
        print("TEST COMPLETE!")
        print("="*50)
        print(f"\nGenerated audio files in: {output_dir.absolute()}")
        print("\nPlease listen to the files and let me know:")
        print("1. Is the voice quality acceptable?")
        print("2. Any specific voice characteristics you'd prefer?")
        print("\nYou can play them with any audio player or run:")
        print(f'  start {output_dir}\\piper_test_1.wav')

        return True

    except Exception as e:
        print(f"Generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("="*50)
    print("PIPER TTS QUALITY TEST")
    print("="*50)
    print()

    # Step 1: Install piper-tts
    if not install_piper():
        print("Failed to install piper-tts. Please check your internet connection.")
        return

    print()

    # Step 2: Download voice model
    model_path = download_voice("en_US-amy-medium")
    if not model_path:
        print("Failed to download voice model.")
        return

    print()

    # Step 3: Generate test audio
    generate_test_audio(model_path)

if __name__ == "__main__":
    main()
