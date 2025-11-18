"""
Base TTS Engine - Abstract interface for all TTS engines
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from pathlib import Path


class BaseTTSEngine(ABC):
    """Abstract base class for TTS engines"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Engine display name"""
        pass

    @property
    @abstractmethod
    def is_online(self) -> bool:
        """Whether this engine requires internet"""
        pass

    @abstractmethod
    def get_voices(self) -> Dict[str, Dict[str, str]]:
        """
        Get available voices organized by category.
        Returns: {category: {voice_id: description}}
        """
        pass

    @abstractmethod
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
        """
        Generate audio from text.

        Args:
            text: Text to convert to speech
            voice: Voice ID to use
            output_path: Path to save audio file
            speed: Speed multiplier (0.5-2.0)
            pitch: Pitch adjustment in Hz (-50 to +50)
            volume: Volume adjustment in % (-50 to +50)
            progress_callback: Optional callback(progress: float, status: str)

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this engine is available (dependencies installed)"""
        pass

    def get_output_extension(self) -> str:
        """Get the output file extension for this engine"""
        return ".mp3"
