from dataclasses import dataclass
import numpy as np

@dataclass
class AudioData:
    """Data class to hold audio waveform and sample rate."""
    path: str
    waveform: np.ndarray
    sample_rate: int
    duration: float = 0.0 # in seconds
    channels: int = 1 # 1 for mono, 2 for stereo

@dataclass
class DenoisingResult:
    """Data class to hold original and denoised audio."""
    original_audio: AudioData
    denoised_audio: AudioData
    noise_profile_segment: np.ndarray = None # The actual noise segment used