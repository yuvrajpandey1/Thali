"""
Text-to-Speech Processor Module
Converts voice scripts to audio using open-source Coqui TTS
"""

import os
import logging
from typing import Optional
import config

logger = logging.getLogger(__name__)

# Try importing TTS, with fallback option
try:
    from TTS.api import TTS
    HAS_TTS = True
except ImportError:
    HAS_TTS = False
    logger.warning("TTS library not installed. Install with: pip install TTS")


class TTSProcessor:
    """Converts text to speech using Coqui TTS"""
    
    def __init__(self):
        self.output_dir = config.AUDIO_OUTPUT_DIR
        self.model_name = config.TTS_MODEL_NAME
        self.speed = config.TTS_SPEED
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.tts_engine = None
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize the TTS engine"""
        if not HAS_TTS:
            logger.warning("TTS engine not available")
            return
        
        try:
            logger.info(f"Initializing TTS with model: {self.model_name}")
            
            # GPU support if available
            gpu = self._check_gpu_available()
            
            self.tts_engine = TTS(
                model_name=self.model_name,
                gpu=gpu,
                verbose=False
            )
            
            logger.info("TTS engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize TTS engine: {str(e)}")
            self.tts_engine = None
    
    def _check_gpu_available(self) -> bool:
        """Check if GPU is available"""
        try:
            import torch
            return torch.cuda.is_available()
        except:
            return False
    
    def text_to_speech(self, text: str, output_file: str = "news_call.wav") -> Optional[str]:
        """
        Convert text to speech
        
        Args:
            text: Text to convert
            output_file: Output audio file name
            
        Returns:
            Path to generated audio file or None if failed
        """
        if not self.tts_engine:
            logger.error("TTS engine not initialized")
            return None
        
        try:
            output_path = os.path.join(self.output_dir, output_file)
            
            logger.info(f"Generating audio: {output_file}")
            logger.debug(f"Text to convert ({len(text)} chars): {text[:100]}...")
            
            # Generate speech
            self.tts_engine.tts_to_file(
                text=text,
                file_path=output_path,
                speaker=config.TTS_SPEAKER,
                language=config.VOICE_LANGUAGE
            )
            
            # Verify file was created
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                logger.info(f"Audio generated successfully: {output_path} ({file_size} bytes)")
                return output_path
            else:
                logger.error("Audio file was not created")
                return None
                
        except Exception as e:
            logger.error(f"Error generating audio: {str(e)}")
            return None
    
    def estimate_duration(self, text: str) -> float:
        """
        Estimate audio duration based on text length
        Average speaking rate: ~150 words per minute = 2.5 words per second
        
        Args:
            text: Text to estimate
            
        Returns:
            Estimated duration in seconds
        """
        word_count = len(text.split())
        # Adjust for speaking rate
        duration = word_count * 0.4  # More conservative estimate
        return duration


class TTSFallback:
    """Fallback TTS using pyttsx3 (no external service required)"""
    
    def __init__(self):
        self.output_dir = config.AUDIO_OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)
        
        try:
            import pyttsx3
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)  # Speech rate
            logger.info("Using pyttsx3 as TTS fallback")
        except Exception as e:
            logger.error(f"Could not initialize pyttsx3: {str(e)}")
            self.engine = None
    
    def text_to_speech(self, text: str, output_file: str = "news_call.wav") -> Optional[str]:
        """Convert text to speech using pyttsx3"""
        if not self.engine:
            logger.error("pyttsx3 engine not available")
            return None
        
        try:
            output_path = os.path.join(self.output_dir, output_file)
            logger.info(f"Generating audio using pyttsx3: {output_file}")
            
            self.engine.save_to_file(text, output_path)
            self.engine.runAndWait()
            
            if os.path.exists(output_path):
                logger.info(f"Audio generated: {output_path}")
                return output_path
            else:
                logger.error("Audio file was not created")
                return None
                
        except Exception as e:
            logger.error(f"Error generating audio: {str(e)}")
            return None


def get_tts_processor():
    """Get appropriate TTS processor"""
    if HAS_TTS:
        return TTSProcessor()
    else:
        logger.info("Falling back to pyttsx3")
        return TTSFallback()


def generate_audio_for_call(voice_script: str) -> Optional[str]:
    """
    Convenience function to generate audio from voice script
    
    Args:
        voice_script: Script to convert to audio
        
    Returns:
        Path to generated audio file or None if failed
    """
    processor = get_tts_processor()
    
    # Truncate script to meet duration requirements
    # Ensure 1-2 minutes (60-120 seconds, ~150-300 words)
    words = voice_script.split()
    if len(words) > 300:
        words = words[:300]
        voice_script = " ".join(words)
    
    logger.info(f"Converting {len(words)} words to audio")
    
    audio_file = processor.text_to_speech(voice_script)
    
    return audio_file
