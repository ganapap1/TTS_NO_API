"""
Piper TTS Engine - Local Neural TTS (Offline)
"""

import os
import wave
import json
import urllib.request
from pathlib import Path
from typing import Dict, Optional, List
from .base_engine import BaseTTSEngine


class PiperTTSEngine(BaseTTSEngine):
    """Piper TTS engine for offline neural TTS"""

    # Models directory
    MODELS_DIR = Path("models/piper")

    # Available Piper voices with download URLs
    PIPER_VOICES = {
        'English (US) - High Quality': {
            'en_US-amy-medium': {
                'name': 'Amy - Female, Clear',
                'url_base': 'https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium',
                'quality': 'medium',
                'bundled': True
            },
            'en_US-ryan-high': {
                'name': 'Ryan - Male, Broadcast',
                'url_base': 'https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/ryan/high',
                'quality': 'high',
                'bundled': True
            },
            'en_US-lessac-high': {
                'name': 'Lessac - Female, Expressive',
                'url_base': 'https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/high',
                'quality': 'high',
                'bundled': True
            },
        },
        'English (UK) - High Quality': {
            'en_GB-cori-high': {
                'name': 'Cori - Female, British',
                'url_base': 'https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/cori/high',
                'quality': 'high',
                'bundled': True
            },
            'en_GB-alan-medium': {
                'name': 'Alan - Male, British',
                'url_base': 'https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/alan/medium',
                'quality': 'medium',
                'bundled': False
            },
        },
        'English (US) - Additional': {
            'en_US-libritts_r-medium': {
                'name': 'LibriTTS - Neutral',
                'url_base': 'https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/libritts_r/medium',
                'quality': 'medium',
                'bundled': False
            },
            'en_US-hfc_male-medium': {
                'name': 'HFC Male - Male, Clear',
                'url_base': 'https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/hfc_male/medium',
                'quality': 'medium',
                'bundled': False
            },
            'en_US-hfc_female-medium': {
                'name': 'HFC Female - Female, Clear',
                'url_base': 'https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/hfc_female/medium',
                'quality': 'medium',
                'bundled': False
            },
        },
    }

    def __init__(self):
        self.MODELS_DIR.mkdir(parents=True, exist_ok=True)
        self._loaded_voice = None
        self._loaded_voice_id = None

    @property
    def name(self) -> str:
        return "Piper (Offline)"

    @property
    def is_online(self) -> bool:
        return False

    def get_voices(self) -> Dict[str, Dict[str, str]]:
        """Get Piper voices organized by category"""
        result = {}
        for category, voices in self.PIPER_VOICES.items():
            result[category] = {}
            for voice_id, info in voices.items():
                # Check if downloaded
                status = " [Downloaded]" if self.is_voice_downloaded(voice_id) else " [Not Downloaded]"
                bundled = " (Bundled)" if info.get('bundled', False) else ""
                result[category][voice_id] = f"{info['name']}{bundled}{status}"
        return result

    def get_voice_info(self, voice_id: str) -> Optional[dict]:
        """Get info for a specific voice"""
        for category, voices in self.PIPER_VOICES.items():
            if voice_id in voices:
                return voices[voice_id]
        return None

    def is_voice_downloaded(self, voice_id: str) -> bool:
        """Check if a voice model is downloaded"""
        model_path = self.MODELS_DIR / f"{voice_id}.onnx"
        config_path = self.MODELS_DIR / f"{voice_id}.onnx.json"
        return model_path.exists() and config_path.exists()

    def get_bundled_voices(self) -> List[str]:
        """Get list of voices that should be bundled"""
        bundled = []
        for category, voices in self.PIPER_VOICES.items():
            for voice_id, info in voices.items():
                if info.get('bundled', False):
                    bundled.append(voice_id)
        return bundled

    def download_voice(
        self,
        voice_id: str,
        progress_callback: Optional[callable] = None
    ) -> bool:
        """Download a voice model"""
        info = self.get_voice_info(voice_id)
        if not info:
            raise ValueError(f"Unknown voice: {voice_id}")

        model_path = self.MODELS_DIR / f"{voice_id}.onnx"
        config_path = self.MODELS_DIR / f"{voice_id}.onnx.json"

        if self.is_voice_downloaded(voice_id):
            return True

        url_base = info['url_base']
        model_url = f"{url_base}/{voice_id}.onnx"
        config_url = f"{url_base}/{voice_id}.onnx.json"

        try:
            # Download model
            if progress_callback:
                progress_callback(0.1, f"Downloading {voice_id} model...")

            def report_progress(block_num, block_size, total_size):
                if total_size > 0 and progress_callback:
                    progress = min(0.9, (block_num * block_size / total_size) * 0.8 + 0.1)
                    progress_callback(progress, f"Downloading: {int(progress * 100)}%")

            urllib.request.urlretrieve(model_url, model_path, reporthook=report_progress)

            # Download config
            if progress_callback:
                progress_callback(0.95, "Downloading config...")
            urllib.request.urlretrieve(config_url, config_path)

            if progress_callback:
                progress_callback(1.0, "Download complete!")

            return True

        except Exception as e:
            # Clean up partial downloads
            if model_path.exists():
                model_path.unlink()
            if config_path.exists():
                config_path.unlink()
            raise

    def generate(
        self,
        text: str,
        voice: str,
        output_path: str,
        speed: float = 1.0,
        pitch: int = 0,
        volume: int = 0,
        progress_callback: Optional[callable] = None
    ) -> bool:
        """Generate speech using Piper TTS"""
        try:
            from piper import PiperVoice

            # Check if voice is downloaded
            if not self.is_voice_downloaded(voice):
                if progress_callback:
                    progress_callback(0.1, f"Downloading voice {voice}...")
                self.download_voice(voice, progress_callback)

            model_path = self.MODELS_DIR / f"{voice}.onnx"

            if progress_callback:
                progress_callback(0.3, "Loading voice model...")

            # Load voice (cache for reuse)
            if self._loaded_voice_id != voice:
                self._loaded_voice = PiperVoice.load(str(model_path))
                self._loaded_voice_id = voice

            if progress_callback:
                progress_callback(0.5, "Generating speech...")

            # Generate audio
            # Note: Piper doesn't support speed/pitch/volume adjustments directly
            # These would need post-processing (future enhancement)

            with wave.open(output_path, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(self._loaded_voice.config.sample_rate)

                for audio_chunk in self._loaded_voice.synthesize(text):
                    wav_file.writeframes(audio_chunk.audio_int16_bytes)

            if progress_callback:
                progress_callback(1.0, "Complete!")

            return True

        except Exception as e:
            if progress_callback:
                progress_callback(0, f"Error: {str(e)}")
            raise

    def is_available(self) -> bool:
        """Check if piper-tts is installed"""
        try:
            from piper import PiperVoice
            return True
        except ImportError:
            return False

    def get_output_extension(self) -> str:
        return ".wav"
