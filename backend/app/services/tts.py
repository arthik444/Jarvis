"""ElevenLabs Text-to-Speech service for voice responses"""
import base64
import logging
from functools import lru_cache

from elevenlabs import ElevenLabs

from app.config import get_settings

logger = logging.getLogger(__name__)


class TTSService:
    """Service for converting text to speech using ElevenLabs"""

    def __init__(self, api_key: str, voice_id: str):
        """
        Initialize TTS service with API key.
        
        Args:
            api_key: ElevenLabs API key
            voice_id: Voice ID to use for speech synthesis
        """
        self.client = ElevenLabs(api_key=api_key)
        self.voice_id = voice_id
        logger.info(f"✓ ElevenLabs TTS service initialized with voice: {voice_id}")

    def text_to_speech(self, text: str) -> bytes:
        """
        Convert text to speech audio.
        
        Args:
            text: Text to convert to speech
            
        Returns:
            Audio bytes (MP3 format)
        """
        try:
            # Generate audio using streaming API (collects all chunks)
            audio_generator = self.client.text_to_speech.convert(
                voice_id=self.voice_id,
                text=text,
                model_id="eleven_turbo_v2_5",  # Fastest model
                output_format="mp3_44100_128",  # Good quality, reasonable size
            )
            
            # Collect all audio chunks
            audio_bytes = b"".join(audio_generator)
            
            logger.info(f"✓ Generated {len(audio_bytes)} bytes of audio for text: '{text[:50]}...'")
            return audio_bytes
            
        except Exception as e:
            logger.error(f"TTS generation failed: {e}")
            raise

    def text_to_speech_base64(self, text: str) -> str:
        """
        Convert text to speech and encode as base64.
        
        Args:
            text: Text to convert to speech
            
        Returns:
            Base64-encoded audio string
        """
        audio_bytes = self.text_to_speech(text)
        return base64.b64encode(audio_bytes).decode('utf-8')


@lru_cache
def get_tts_service() -> TTSService:
    """
    Get cached TTS service instance.
    
    Returns:
        Configured TTSService instance
        
    Raises:
        ValueError: If ELEVENLABS_API_KEY is not configured
    """
    settings = get_settings()
    
    if not settings.elevenlabs_api_key:
        raise ValueError(
            "ELEVENLABS_API_KEY not configured. "
            "Please add it to your .env file."
        )
    
    return TTSService(
        api_key=settings.elevenlabs_api_key,
        voice_id=settings.elevenlabs_voice_id
    )
