import librosa
import soundfile as sf
import numpy as np
import logging
import os

logger = logging.getLogger(__name__)

class AudioProcessor:
    """Handles loading, saving, and basic audio manipulations."""

    def load_audio(self, file_path: str, sr: int = None) -> tuple[np.ndarray, int]:
        """
        Loads an audio file.
        Args:
            file_path: Path to the audio file.
            sr: Target sample rate. If None, uses original sample rate.
        Returns:
            Tuple of (waveform, sample_rate).
        Raises:
            FileNotFoundError, Exception for unsupported formats.
        """
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        try:
            # librosa loads as mono by default, and resamples if sr is specified
            waveform, sample_rate = librosa.load(file_path, sr=sr, mono=True)
            logger.info(f"Loaded audio: {file_path}, SR: {sample_rate}, Duration: {len(waveform)/sample_rate:.2f}s")
            return waveform, sample_rate
        except Exception as e:
            logger.error(f"Error loading audio file {file_path}: {e}")
            raise ValueError(f"Could not load audio file. Is it a supported format? Error: {e}")

    def save_audio(self, waveform: np.ndarray, sample_rate: int, output_path: str):
        """
        Saves a waveform to an audio file.
        Args:
            waveform: The audio waveform (numpy array).
            sample_rate: The sample rate of the waveform.
            output_path: The path to save the audio file (e.g., "output.wav").
        """
        try:
            sf.write(output_path, waveform, sample_rate)
            logger.info(f"Saved audio to: {output_path}")
        except Exception as e:
            logger.error(f"Error saving audio to {output_path}: {e}")
            raise IOError(f"Could not save audio file. Error: {e}")

    def extract_noise_profile(self, waveform: np.ndarray, sample_rate: int, duration_s: float = 0.5) -> np.ndarray:
        """
        Extracts a noise profile from the beginning of the audio.
        This is a simplified placeholder. More advanced methods would involve VAD.
        """
        num_samples = int(duration_s * sample_rate)
        noise_segment = waveform[:min(num_samples, len(waveform))]
        logger.info(f"Extracted noise profile from first {len(noise_segment)/sample_rate:.2f} seconds.")
        return noise_segment

    # Placeholder for actual denoising logic (will be in deepfilternet_service.py etc.)
    def apply_denoising_placeholder(self, waveform: np.ndarray, sample_rate: int, noise_profile: np.ndarray) -> np.ndarray:
        """
        A placeholder for denoising. In a real scenario, this would call an AI model.
        For now, it just returns the original waveform.
        """
        logger.warning("Using placeholder denoising. No actual noise reduction applied.")
        # Simulate some processing time
        import time
        time.sleep(2)
        return waveform * 0.8 # Just to show a slight change