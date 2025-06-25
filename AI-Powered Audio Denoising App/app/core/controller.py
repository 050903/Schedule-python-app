from PyQt6.QtCore import QObject, pyqtSignal, QThreadPool
from services.audio_processor import AudioProcessor
from models.audio_data import AudioData, DenoisingResult
from core.worker import Worker
import logging
import numpy as np

logger = logging.getLogger(__name__)

class ApplicationController(QObject):
    """
    Manages the application's logic, acting as a bridge between the UI (View)
    and the data/service layers (Model).
    """
    audio_loaded = pyqtSignal(AudioData)
    status_updated = pyqtSignal(str)
    progress_updated = pyqtSignal(int) # 0-100
    error_occurred = pyqtSignal(str)
    denoising_finished = pyqtSignal(DenoisingResult)

    def __init__(self):
        super().__init__()
        self.audio_processor = AudioProcessor()
        self.thread_pool = QThreadPool()
        logger.info(f"Initialized ApplicationController with {self.thread_pool.maxThreadCount()} threads available.")

        self.current_audio: AudioData = None
        self.denoised_audio: AudioData = None

    def load_audio_file(self, file_path: str):
        """Loads an audio file in a separate thread."""
        self.status_updated.emit(f"Loading audio from: {file_path}...")
        self.progress_updated.emit(0)

        def _load_audio_task(progress_callback, status_callback):
            try:
                status_callback("Loading audio...")
                waveform, sample_rate = self.audio_processor.load_audio(file_path)
                duration = len(waveform) / sample_rate
                audio_data = AudioData(file_path, waveform, sample_rate, duration)
                progress_callback(100)
                status_callback("Audio loaded successfully.")
                return audio_data
            except Exception as e:
                status_callback(f"Error loading audio: {e}")
                raise # Re-raise to be caught by worker's error signal

        worker = Worker(_load_audio_task)
        worker.signals.result.connect(self._on_audio_load_success)
        worker.signals.error.connect(self._on_task_error)
        worker.signals.progress.connect(self.progress_updated)
        worker.signals.status.connect(self.status_updated)
        self.thread_pool.start(worker)

    def _on_audio_load_success(self, audio_data: AudioData):
        self.current_audio = audio_data
        self.audio_loaded.emit(audio_data)
        logger.info(f"Audio data set: {audio_data.path}")

    def _on_task_error(self, error_tuple):
        exctype, value, tb_str = error_tuple
        error_message = f"An error occurred: {value}\n{tb_str}"
        logger.error(error_message)
        self.error_occurred.emit(str(value))
        self.status_updated.emit(f"Error: {value}")
        self.progress_updated.emit(0) # Reset progress

    def analyze_and_preview_noise(self):
        """Analyzes noise profile and prepares for preview."""
        if not self.current_audio:
            self.error_occurred.emit("No audio loaded to analyze noise.")
            self.status_updated.emit("Error: No audio loaded.")
            return

        self.status_updated.emit("Analyzing noise profile...")
        self.progress_updated.emit(0)

        def _analyze_noise_task(progress_callback, status_callback):
            status_callback("Extracting noise segment...")
            noise_segment = self.audio_processor.extract_noise_profile(
                self.current_audio.waveform, self.current_audio.sample_rate
            )
            progress_callback(100)
            status_callback("Noise profile analyzed. Ready to preview.")
            return noise_segment

        worker = Worker(_analyze_noise_task)
        worker.signals.result.connect(self._on_noise_analysis_success)
        worker.signals.error.connect(self._on_task_error)
        worker.signals.progress.connect(self.progress_updated)
        worker.signals.status.connect(self.status_updated)
        self.thread_pool.start(worker)

    def _on_noise_analysis_success(self, noise_segment: np.ndarray):
        # In a real app, you'd store this and enable a "Play Noise" button
        logger.info(f"Noise segment extracted (length: {len(noise_segment)} samples).")
        self.status_updated.emit("Noise profile ready for preview.")
        # For now, we just log it. Later, emit a signal to play this segment.

    def process_denoising(self):
        """Initiates the denoising process in a separate thread."""
        if not self.current_audio:
            self.error_occurred.emit("No audio loaded to denoise.")
            self.status_updated.emit("Error: No audio loaded.")
            return

        self.status_updated.emit("Starting denoising process...")
        self.progress_updated.emit(0)

        def _denoise_task(progress_callback, status_callback):
            status_callback("Applying denoising model (placeholder)...")
            # In a real scenario, you'd call deepfilternet_service.denoise_audio here
            # For now, using a placeholder from audio_processor
            noise_profile = self.audio_processor.extract_noise_profile(
                self.current_audio.waveform, self.current_audio.sample_rate
            )
            denoised_waveform = self.audio_processor.apply_denoising_placeholder(
                self.current_audio.waveform, self.current_audio.sample_rate, noise_profile
            )
            progress_callback(100)
            status_callback("Denoising complete.")
            return denoised_waveform

        worker = Worker(_denoise_task)
        worker.signals.result.connect(self._on_denoising_success)
        worker.signals.error.connect(self._on_task_error)
        worker.signals.progress.connect(self.progress_updated)
        worker.signals.status.connect(self.status_updated)
        self.thread_pool.start(worker)

    def _on_denoising_success(self, denoised_waveform: np.ndarray):
        self.denoised_audio = AudioData(
            path=self.current_audio.path + "_denoised", # Placeholder path
            waveform=denoised_waveform,
            sample_rate=self.current_audio.sample_rate,
            duration=len(denoised_waveform) / self.current_audio.sample_rate
        )
        result = DenoisingResult(self.current_audio, self.denoised_audio)
        self.denoising_finished.emit(result)
        logger.info("Denoising process finished successfully.")
        self.status_updated.emit("Denoising complete. Ready for comparison and export.")

    def export_audio(self, output_path: str):
        """Exports the denoised audio."""
        if not self.denoised_audio:
            self.error_occurred.emit("No denoised audio to export.")
            self.status_updated.emit("Error: No denoised audio.")
            return

        self.status_updated.emit(f"Exporting audio to: {output_path}...")
        self.progress_updated.emit(0)

        def _export_audio_task(progress_callback, status_callback):
            status_callback("Saving denoised audio...")
            self.audio_processor.save_audio(
                self.denoised_audio.waveform,
                self.denoised_audio.sample_rate,
                output_path
            )
            progress_callback(100)
            status_callback(f"Audio exported successfully to {output_path}.")
            return True

        worker = Worker(_export_audio_task)
        worker.signals.result.connect(lambda: logger.info("Export task finished."))
        worker.signals.error.connect(self._on_task_error)
        worker.signals.progress.connect(self.progress_updated)
        worker.signals.status.connect(self.status_updated)
        self.thread_pool.start(worker)