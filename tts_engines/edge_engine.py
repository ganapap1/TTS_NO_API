"""
Edge TTS Engine - Microsoft Edge Neural Voices (Online)
"""

import asyncio
from typing import Dict, Optional
from .base_engine import BaseTTSEngine


class EdgeTTSEngine(BaseTTSEngine):
    """Edge TTS engine using Microsoft Edge Neural Voices"""

    @property
    def name(self) -> str:
        return "Edge TTS (Online)"

    @property
    def is_online(self) -> bool:
        return True

    def get_voices(self) -> Dict[str, Dict[str, str]]:
        """Get Edge TTS voices organized by category"""
        return {
            'English (US)': {
                'en-US-JennyNeural': 'Jenny - Female, Friendly',
                'en-US-GuyNeural': 'Guy - Male, Professional',
                'en-US-AriaNeural': 'Aria - Female, Natural',
                'en-US-DavisNeural': 'Davis - Male, Calm',
                'en-US-AmberNeural': 'Amber - Female, Warm',
                'en-US-AnaNeural': 'Ana - Female, Child',
                'en-US-AndrewNeural': 'Andrew - Male, Warm',
                'en-US-EmmaNeural': 'Emma - Female, Clear',
                'en-US-BrianNeural': 'Brian - Male, Casual',
                'en-US-ChristopherNeural': 'Christopher - Male, Authoritative',
                'en-US-EricNeural': 'Eric - Male, Friendly',
                'en-US-MichelleNeural': 'Michelle - Female, Professional',
                'en-US-RogerNeural': 'Roger - Male, Elderly',
                'en-US-SteffanNeural': 'Steffan - Male, News',
            },
            'English (UK)': {
                'en-GB-SoniaNeural': 'Sonia - Female, British',
                'en-GB-RyanNeural': 'Ryan - Male, British',
                'en-GB-LibbyNeural': 'Libby - Female, British Warm',
                'en-GB-MaisieNeural': 'Maisie - Female, Child',
                'en-GB-ThomasNeural': 'Thomas - Male, British Friendly',
            },
            'English (Australia)': {
                'en-AU-NatashaNeural': 'Natasha - Female, Australian',
                'en-AU-WilliamNeural': 'William - Male, Australian',
            },
            'English (India)': {
                'en-IN-NeerjaNeural': 'Neerja - Female, Indian',
                'en-IN-PrabhatNeural': 'Prabhat - Male, Indian',
            },
            'English (Other)': {
                'en-CA-ClaraNeural': 'Clara - Female, Canadian',
                'en-CA-LiamNeural': 'Liam - Male, Canadian',
                'en-IE-EmilyNeural': 'Emily - Female, Irish',
                'en-IE-ConnorNeural': 'Connor - Male, Irish',
                'en-NZ-MollyNeural': 'Molly - Female, New Zealand',
                'en-NZ-MitchellNeural': 'Mitchell - Male, New Zealand',
                'en-ZA-LeahNeural': 'Leah - Female, South African',
                'en-ZA-LukeNeural': 'Luke - Male, South African',
            },
        }

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
        """Generate speech using Edge TTS"""
        try:
            import edge_tts

            # Convert parameters to Edge TTS format
            rate_percent = int((speed - 1.0) * 100)
            rate = f"+{rate_percent}%" if rate_percent >= 0 else f"{rate_percent}%"
            pitch_str = f"+{pitch}Hz" if pitch >= 0 else f"{pitch}Hz"
            volume_str = f"+{volume}%" if volume >= 0 else f"{volume}%"

            if progress_callback:
                progress_callback(0.2, "Connecting to Edge TTS...")

            async def run_edge_tts():
                communicate = edge_tts.Communicate(
                    text,
                    voice,
                    rate=rate,
                    pitch=pitch_str,
                    volume=volume_str
                )
                await communicate.save(output_path)

            if progress_callback:
                progress_callback(0.5, "Generating speech...")

            asyncio.run(run_edge_tts())

            if progress_callback:
                progress_callback(1.0, "Complete!")

            return True

        except Exception as e:
            if progress_callback:
                progress_callback(0, f"Error: {str(e)}")
            raise

    def is_available(self) -> bool:
        """Check if edge-tts is installed"""
        try:
            import edge_tts
            return True
        except ImportError:
            return False

    def get_output_extension(self) -> str:
        return ".mp3"
