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

# Optional language detection
try:
    from langdetect import detect, LangDetectException
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False


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
        'French': {
            'fr_FR-siwis-medium': {
                'name': 'Siwis - Female, French',
                'url_base': 'https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/siwis/medium',
                'quality': 'medium',
                'bundled': False
            },
            'fr_FR-upmc-medium': {
                'name': 'UPMC - Male, French',
                'url_base': 'https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/upmc/medium',
                'quality': 'medium',
                'bundled': False
            },
        },
        'Italian': {
            'it_IT-riccardo-x_low': {
                'name': 'Riccardo - Male, Italian',
                'url_base': 'https://huggingface.co/rhasspy/piper-voices/resolve/main/it/it_IT/riccardo/x_low',
                'quality': 'x_low',
                'bundled': False
            },
        },
        'Spanish': {
            'es_ES-davefx-medium': {
                'name': 'Davefx - Male, Spanish (Spain)',
                'url_base': 'https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/davefx/medium',
                'quality': 'medium',
                'bundled': False
            },
            'es_MX-ald-medium': {
                'name': 'Ald - Female, Spanish (Mexico)',
                'url_base': 'https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_MX/ald/medium',
                'quality': 'medium',
                'bundled': False
            },
        },
        'German': {
            'de_DE-thorsten-medium': {
                'name': 'Thorsten - Male, German',
                'url_base': 'https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/medium',
                'quality': 'medium',
                'bundled': False
            },
            'de_DE-eva_k-x_low': {
                'name': 'Eva K - Female, German',
                'url_base': 'https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/eva_k/x_low',
                'quality': 'x_low',
                'bundled': False
            },
        },
        'Portuguese': {
            'pt_BR-faber-medium': {
                'name': 'Faber - Male, Portuguese (Brazil)',
                'url_base': 'https://huggingface.co/rhasspy/piper-voices/resolve/main/pt/pt_BR/faber/medium',
                'quality': 'medium',
                'bundled': False
            },
        },
        'Russian': {
            'ru_RU-dmitri-medium': {
                'name': 'Dmitri - Male, Russian',
                'url_base': 'https://huggingface.co/rhasspy/piper-voices/resolve/main/ru/ru_RU/dmitri/medium',
                'quality': 'medium',
                'bundled': False
            },
            'ru_RU-irina-medium': {
                'name': 'Irina - Female, Russian',
                'url_base': 'https://huggingface.co/rhasspy/piper-voices/resolve/main/ru/ru_RU/irina/medium',
                'quality': 'medium',
                'bundled': False
            },
        },
        'Chinese': {
            'zh_CN-huayan-medium': {
                'name': 'Huayan - Female, Chinese',
                'url_base': 'https://huggingface.co/rhasspy/piper-voices/resolve/main/zh/zh_CN/huayan/medium',
                'quality': 'medium',
                'bundled': False
            },
        },
        'Japanese': {
            'ja_JP-kokoro-medium': {
                'name': 'Kokoro - Female, Japanese',
                'url_base': 'https://huggingface.co/rhasspy/piper-voices/resolve/main/ja/ja_JP/kokoro/medium',
                'quality': 'medium',
                'bundled': False
            },
        },
        'Korean': {
            'ko_KR-kagayaki-medium': {
                'name': 'Kagayaki - Female, Korean',
                'url_base': 'https://huggingface.co/rhasspy/piper-voices/resolve/main/ko/ko_KR/kagayaki/medium',
                'quality': 'medium',
                'bundled': False
            },
        },
        'Dutch': {
            'nl_NL-mls-medium': {
                'name': 'MLS - Neutral, Dutch',
                'url_base': 'https://huggingface.co/rhasspy/piper-voices/resolve/main/nl/nl_NL/mls/medium',
                'quality': 'medium',
                'bundled': False
            },
        },
        'Polish': {
            'pl_PL-gosia-medium': {
                'name': 'Gosia - Female, Polish',
                'url_base': 'https://huggingface.co/rhasspy/piper-voices/resolve/main/pl/pl_PL/gosia/medium',
                'quality': 'medium',
                'bundled': False
            },
        },
        'Ukrainian': {
            'uk_UA-ukrainian_tts-medium': {
                'name': 'Ukrainian TTS - Neutral',
                'url_base': 'https://huggingface.co/rhasspy/piper-voices/resolve/main/uk/uk_UA/ukrainian_tts/medium',
                'quality': 'medium',
                'bundled': False
            },
        },
        'Turkish': {
            'tr_TR-dfki-medium': {
                'name': 'DFKI - Male, Turkish',
                'url_base': 'https://huggingface.co/rhasspy/piper-voices/resolve/main/tr/tr_TR/dfki/medium',
                'quality': 'medium',
                'bundled': False
            },
        },
        'Vietnamese': {
            'vi_VN-vivos-x_low': {
                'name': 'Vivos - Neutral, Vietnamese',
                'url_base': 'https://huggingface.co/rhasspy/piper-voices/resolve/main/vi/vi_VN/vivos/x_low',
                'quality': 'x_low',
                'bundled': False
            },
        },
        'Czech': {
            'cs_CZ-jirka-medium': {
                'name': 'Jirka - Male, Czech',
                'url_base': 'https://huggingface.co/rhasspy/piper-voices/resolve/main/cs/cs_CZ/jirka/medium',
                'quality': 'medium',
                'bundled': False
            },
        },
        'Danish': {
            'da_DK-talesyntese-medium': {
                'name': 'Talesyntese - Neutral, Danish',
                'url_base': 'https://huggingface.co/rhasspy/piper-voices/resolve/main/da/da_DK/talesyntese/medium',
                'quality': 'medium',
                'bundled': False
            },
        },
        'Finnish': {
            'fi_FI-harri-medium': {
                'name': 'Harri - Male, Finnish',
                'url_base': 'https://huggingface.co/rhasspy/piper-voices/resolve/main/fi/fi_FI/harri/medium',
                'quality': 'medium',
                'bundled': False
            },
        },
        'Greek': {
            'el_GR-rapunzelina-low': {
                'name': 'Rapunzelina - Female, Greek',
                'url_base': 'https://huggingface.co/rhasspy/piper-voices/resolve/main/el/el_GR/rapunzelina/low',
                'quality': 'low',
                'bundled': False
            },
        },
        'Hungarian': {
            'hu_HU-anna-medium': {
                'name': 'Anna - Female, Hungarian',
                'url_base': 'https://huggingface.co/rhasspy/piper-voices/resolve/main/hu/hu_HU/anna/medium',
                'quality': 'medium',
                'bundled': False
            },
        },
        'Norwegian': {
            'nb_NO-talesyntese-medium': {
                'name': 'Talesyntese - Neutral, Norwegian',
                'url_base': 'https://huggingface.co/rhasspy/piper-voices/resolve/main/nb/nb_NO/talesyntese/medium',
                'quality': 'medium',
                'bundled': False
            },
        },
        'Romanian': {
            'ro_RO-mihai-medium': {
                'name': 'Mihai - Male, Romanian',
                'url_base': 'https://huggingface.co/rhasspy/piper-voices/resolve/main/ro/ro_RO/mihai/medium',
                'quality': 'medium',
                'bundled': False
            },
        },
        'Swedish': {
            'sv_SE-nst-medium': {
                'name': 'NST - Neutral, Swedish',
                'url_base': 'https://huggingface.co/rhasspy/piper-voices/resolve/main/sv/sv_SE/nst/medium',
                'quality': 'medium',
                'bundled': False
            },
        },
        'Catalan': {
            'ca_ES-upc_ona-medium': {
                'name': 'UPC Ona - Female, Catalan',
                'url_base': 'https://huggingface.co/rhasspy/piper-voices/resolve/main/ca/ca_ES/upc_ona/medium',
                'quality': 'medium',
                'bundled': False
            },
        },
        'Arabic': {
            'ar_JO-kareem-medium': {
                'name': 'Kareem - Male, Arabic',
                'url_base': 'https://huggingface.co/rhasspy/piper-voices/resolve/main/ar/ar_JO/kareem/medium',
                'quality': 'medium',
                'bundled': False
            },
        },
        'Icelandic': {
            'is_IS-bui-medium': {
                'name': 'Bui - Male, Icelandic',
                'url_base': 'https://huggingface.co/rhasspy/piper-voices/resolve/main/is/is_IS/bui/medium',
                'quality': 'medium',
                'bundled': False
            },
        },
        'Slovak': {
            'sk_SK-lili-medium': {
                'name': 'Lili - Female, Slovak',
                'url_base': 'https://huggingface.co/rhasspy/piper-voices/resolve/main/sk/sk_SK/lili/medium',
                'quality': 'medium',
                'bundled': False
            },
        },
        'Slovenian': {
            'sl_SI-artur-medium': {
                'name': 'Artur - Male, Slovenian',
                'url_base': 'https://huggingface.co/rhasspy/piper-voices/resolve/main/sl/sl_SI/artur/medium',
                'quality': 'medium',
                'bundled': False
            },
        },
        'Serbian': {
            'sr_RS-serbski_institut-medium': {
                'name': 'Serbski Institut - Neutral, Serbian',
                'url_base': 'https://huggingface.co/rhasspy/piper-voices/resolve/main/sr/sr_RS/serbski_institut/medium',
                'quality': 'medium',
                'bundled': False
            },
        },
        'Swahili': {
            'sw_CD-lanfrica-medium': {
                'name': 'Lanfrica - Neutral, Swahili',
                'url_base': 'https://huggingface.co/rhasspy/piper-voices/resolve/main/sw/sw_CD/lanfrica/medium',
                'quality': 'medium',
                'bundled': False
            },
        },
        'Georgian': {
            'ka_GE-natia-medium': {
                'name': 'Natia - Female, Georgian',
                'url_base': 'https://huggingface.co/rhasspy/piper-voices/resolve/main/ka/ka_GE/natia/medium',
                'quality': 'medium',
                'bundled': False
            },
        },
        'Kazakh': {
            'kk_KZ-iseke-x_low': {
                'name': 'Iseke - Male, Kazakh',
                'url_base': 'https://huggingface.co/rhasspy/piper-voices/resolve/main/kk/kk_KZ/iseke/x_low',
                'quality': 'x_low',
                'bundled': False
            },
        },
        'Nepali': {
            'ne_NP-google-medium': {
                'name': 'Google - Neutral, Nepali',
                'url_base': 'https://huggingface.co/rhasspy/piper-voices/resolve/main/ne/ne_NP/google/medium',
                'quality': 'medium',
                'bundled': False
            },
        },
        'Welsh': {
            'cy_GB-gwryw_gogleddol-medium': {
                'name': 'Gwryw Gogleddol - Male, Welsh',
                'url_base': 'https://huggingface.co/rhasspy/piper-voices/resolve/main/cy/cy_GB/gwryw_gogleddol/medium',
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

        # Add predefined voices from PIPER_VOICES
        for category, voices in self.PIPER_VOICES.items():
            result[category] = {}
            for voice_id, info in voices.items():
                # Check if downloaded
                status = " [Downloaded]" if self.is_voice_downloaded(voice_id) else " [Not Downloaded]"
                bundled = " (Bundled)" if info.get('bundled', False) else ""
                result[category][voice_id] = f"{info['name']}{bundled}{status}"

        # Auto-detect manually added voice files
        manually_added = self._detect_manual_voices()
        if manually_added:
            result['Manually Added Voices'] = {}
            for voice_id, name in manually_added.items():
                result['Manually Added Voices'][voice_id] = f"{name} [Downloaded]"

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

    def _detect_manual_voices(self) -> Dict[str, str]:
        """Detect voice files that were manually added to models/piper/"""
        manual_voices = {}

        # Get all predefined voice IDs
        predefined_ids = set()
        for category, voices in self.PIPER_VOICES.items():
            predefined_ids.update(voices.keys())

        # Scan the models directory for .onnx files
        if not self.MODELS_DIR.exists():
            return manual_voices

        for onnx_file in self.MODELS_DIR.glob("*.onnx"):
            # Skip if it's just a config file
            if onnx_file.name.endswith(".onnx.json"):
                continue

            voice_id = onnx_file.stem  # Remove .onnx extension
            config_file = self.MODELS_DIR / f"{voice_id}.onnx.json"

            # Only include if both model and config exist AND it's not predefined
            if config_file.exists() and voice_id not in predefined_ids:
                # Try to parse a friendly name from the voice_id
                # Format: en_US-amy-medium -> Amy (US, Medium)
                name = self._parse_voice_name(voice_id)
                manual_voices[voice_id] = name

        return manual_voices

    def _parse_voice_name(self, voice_id: str) -> str:
        """Parse a friendly name from voice_id"""
        try:
            # Example: es_ES-davefx-medium -> Spanish (ES, Davefx, Medium)
            # Example: it_IT-riccardo-x_low -> Italian (IT, Riccardo, X Low)
            parts = voice_id.split('-')
            if len(parts) >= 2:
                locale = parts[0]  # e.g., es_ES, it_IT
                voice_name = parts[1] if len(parts) > 1 else "Unknown"
                quality = parts[2] if len(parts) > 2 else ""

                # Extract language from locale
                lang_code = locale.split('_')[0].upper()
                country_code = locale.split('_')[1].upper() if '_' in locale else ""

                # Language name mapping
                lang_map = {
                    'ES': 'Spanish', 'IT': 'Italian', 'FR': 'French', 'DE': 'German',
                    'PT': 'Portuguese', 'RU': 'Russian', 'ZH': 'Chinese', 'JA': 'Japanese',
                    'KO': 'Korean', 'NL': 'Dutch', 'PL': 'Polish', 'UK': 'Ukrainian',
                    'VI': 'Vietnamese', 'AR': 'Arabic', 'TR': 'Turkish', 'HI': 'Hindi',
                    'CS': 'Czech', 'DA': 'Danish', 'FI': 'Finnish', 'EL': 'Greek',
                    'HU': 'Hungarian', 'IS': 'Icelandic', 'NB': 'Norwegian', 'RO': 'Romanian',
                    'SK': 'Slovak', 'SV': 'Swedish', 'SW': 'Swahili', 'KA': 'Georgian'
                }

                lang_name = lang_map.get(lang_code, lang_code)

                # Format voice name nicely
                voice_display = voice_name.replace('_', ' ').title()
                quality_display = quality.replace('_', ' ').title() if quality else ""

                if quality_display:
                    return f"{voice_display} - {lang_name} ({country_code}, {quality_display})"
                else:
                    return f"{voice_display} - {lang_name} ({country_code})"
            else:
                return voice_id.replace('_', ' ').title()
        except:
            return voice_id

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

    def has_downloaded_voices_for_language(self, lang_code: str) -> bool:
        """Check if any voices are downloaded for a specific language"""
        all_voices = self.get_voices()
        for category, voices in all_voices.items():
            for voice_id, voice_desc in voices.items():
                voice_lang = self.get_voice_language(voice_id)
                if voice_lang == lang_code and self.is_voice_downloaded(voice_id):
                    return True
        return False

    def get_downloaded_languages(self) -> List[str]:
        """Get list of language codes that have at least one downloaded voice"""
        languages = set()
        all_voices = self.get_voices()
        for category, voices in all_voices.items():
            for voice_id in voices.keys():
                if self.is_voice_downloaded(voice_id):
                    lang = self.get_voice_language(voice_id)
                    if lang:
                        languages.add(lang)
        return list(languages)

    @staticmethod
    def is_langdetect_available() -> bool:
        """Check if langdetect library is available"""
        return LANGDETECT_AVAILABLE

    @staticmethod
    def detect_language(text: str) -> Optional[str]:
        """Detect language from text. Returns ISO 639-1 code (e.g., 'en', 'es', 'it')"""
        if not LANGDETECT_AVAILABLE or not text or len(text.strip()) < 10:
            return None
        try:
            return detect(text)
        except (LangDetectException, Exception):
            return None

    def get_voice_language(self, voice_id: str) -> Optional[str]:
        """Extract language code from voice_id (e.g., 'en_US-amy-medium' -> 'en')"""
        try:
            # Extract locale part (e.g., 'en_US', 'es_ES', 'it_IT')
            parts = voice_id.split('-')
            if len(parts) > 0:
                locale = parts[0]  # e.g., 'en_US'
                lang_code = locale.split('_')[0].lower()  # e.g., 'en'
                return lang_code
        except:
            pass
        return None

    def get_voices_by_language(self, lang_code: Optional[str] = None, show_all: bool = False) -> Dict[str, Dict[str, str]]:
        """
        Get voices filtered by language or grouped by language.

        Args:
            lang_code: ISO 639-1 language code (e.g., 'en', 'es', 'it'). None to show all.
            show_all: If True, returns voices grouped by language with separators

        Returns:
            Dictionary of voices organized by category
        """
        all_voices = self.get_voices()

        # If showing all with grouping
        if show_all:
            return self._group_voices_by_language(all_voices)

        # If filtering by language
        if lang_code:
            return self._filter_voices_by_language(all_voices, lang_code)

        # Default: return all voices ungrouped
        return all_voices

    def _filter_voices_by_language(self, all_voices: Dict[str, Dict[str, str]], lang_code: str) -> Dict[str, Dict[str, str]]:
        """Filter voices to show only those matching the language code"""
        filtered = {}

        for category, voices in all_voices.items():
            filtered_category = {}
            for voice_id, voice_desc in voices.items():
                voice_lang = self.get_voice_language(voice_id)
                if voice_lang == lang_code:
                    filtered_category[voice_id] = voice_desc

            if filtered_category:  # Only add category if it has voices
                filtered[category] = filtered_category

        return filtered if filtered else all_voices  # Fallback to all if no matches

    def _group_voices_by_language(self, all_voices: Dict[str, Dict[str, str]]) -> Dict[str, Dict[str, str]]:
        """Group all voices by language with visual separators"""
        # Collect all voices with their languages
        voices_by_lang = {}

        for category, voices in all_voices.items():
            for voice_id, voice_desc in voices.items():
                voice_lang = self.get_voice_language(voice_id)
                if voice_lang:
                    if voice_lang not in voices_by_lang:
                        voices_by_lang[voice_lang] = []
                    voices_by_lang[voice_lang].append((voice_id, voice_desc))

        # Build grouped result with separators
        result = {}
        lang_names = {
            'en': 'English',
            'es': 'Spanish',
            'it': 'Italian',
            'fr': 'French',
            'de': 'German',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'zh': 'Chinese',
            'ja': 'Japanese',
            'ko': 'Korean',
            'nl': 'Dutch',
            'pl': 'Polish',
            'uk': 'Ukrainian',
            'vi': 'Vietnamese',
            'ar': 'Arabic',
            'tr': 'Turkish',
            'hi': 'Hindi',
            'cs': 'Czech',
            'da': 'Danish',
            'fi': 'Finnish',
            'el': 'Greek',
            'hu': 'Hungarian',
            'is': 'Icelandic',
            'nb': 'Norwegian',
            'ro': 'Romanian',
            'sk': 'Slovak',
            'sv': 'Swedish',
            'sw': 'Swahili',
            'ka': 'Georgian'
        }

        # Sort languages alphabetically
        sorted_langs = sorted(voices_by_lang.keys(), key=lambda x: lang_names.get(x, x))

        for lang_code in sorted_langs:
            lang_name = lang_names.get(lang_code, lang_code.upper())
            category_name = f"──── {lang_name} ────"

            result[category_name] = {}
            for voice_id, voice_desc in sorted(voices_by_lang[lang_code], key=lambda x: x[1]):
                # Add indentation to voice description
                result[category_name][voice_id] = f"  {voice_desc}"

        return result
