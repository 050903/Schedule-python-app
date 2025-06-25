import sys
from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton,
    QTextEdit, QProgressBar, QFileDialog, QLabel, QSizePolicy, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSlot, QUrl
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QPalette, QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
import logging

from core.controller import ApplicationController
from models.audio_data import AudioData, DenoisingResult

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    def __init__(self, controller: ApplicationController):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("AI Audio Denoising App")
        self.setGeometry(100, 100, 1000, 700)

        self.current_audio_data: AudioData = None
        self.denoised_audio_data: AudioData = None

        self.init_ui()
        self.apply_dark_theme() # Default to dark theme
        self.setAcceptDrops(True) # Enable drag and drop

        # Ép cửa sổ hiện lên và luôn ở trên cùng
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self.raise_()
        self.activateWindow()
        self.move(100, 100)  # Đảm bảo cửa sổ nằm trong vùng nhìn thấy

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- Top Controls ---
        top_controls_layout = QHBoxLayout()
        self.load_audio_btn = QPushButton("Load Audio")
        self.load_audio_btn.clicked.connect(self.load_audio_file)
        top_controls_layout.addWidget(self.load_audio_btn)

        self.analyze_btn = QPushButton("Analyze/Preview Noise")
        self.analyze_btn.clicked.connect(self.controller.analyze_and_preview_noise)
        self.analyze_btn.setEnabled(False) # Disabled until audio loaded
        top_controls_layout.addWidget(self.analyze_btn)

        self.denoise_btn = QPushButton("Denoise")
        self.denoise_btn.clicked.connect(self.controller.process_denoising)
        self.denoise_btn.setEnabled(False) # Disabled until audio loaded
        top_controls_layout.addWidget(self.denoise_btn)

        self.compare_btn = QPushButton("Compare")
        self.compare_btn.clicked.connect(self.compare_audio)
        self.compare_btn.setEnabled(False) # Disabled until denoised
        top_controls_layout.addWidget(self.compare_btn)

        self.export_btn = QPushButton("Export")
        self.export_btn.clicked.connect(self.export_cleaned_audio)
        self.export_btn.setEnabled(False) # Disabled until denoised
        top_controls_layout.addWidget(self.export_btn)

        self.theme_toggle_btn = QPushButton("Toggle Theme")
        self.theme_toggle_btn.clicked.connect(self.toggle_theme)
        top_controls_layout.addWidget(self.theme_toggle_btn)

        main_layout.addLayout(top_controls_layout)

        # --- Waveform Visualization ---
        self.fig = Figure(figsize=(10, 4))
        self.canvas = FigureCanvas(self.fig)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Waveform Visualization")
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Amplitude")
        self.ax.grid(True)
        self.fig.tight_layout()
        main_layout.addWidget(self.canvas)

        # --- Audio Playback Controls (Placeholder) ---
        playback_layout = QHBoxLayout()
        self.play_original_btn = QPushButton("Play Original")
        self.play_original_btn.setEnabled(False)
        playback_layout.addWidget(self.play_original_btn)

        self.play_denoised_btn = QPushButton("Play Denoised")
        self.play_denoised_btn.setEnabled(False)
        playback_layout.addWidget(self.play_denoised_btn)

        self.stop_playback_btn = QPushButton("Stop")
        self.stop_playback_btn.setEnabled(False)
        playback_layout.addWidget(self.stop_playback_btn)

        self.seek_slider = QLabel("Seek Bar (Coming Soon)") # Placeholder
        playback_layout.addWidget(self.seek_slider)
        main_layout.addLayout(playback_layout)


        # --- Progress Bar ---
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("Ready")
        main_layout.addWidget(self.progress_bar)

        # --- Status Log ---
        self.status_log = QTextEdit()
        self.status_log.setReadOnly(True)
        self.status_log.setPlaceholderText("Application status and logs will appear here...")
        self.status_log.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.status_log.setFixedHeight(100) # Fixed height for log
        main_layout.addWidget(self.status_log)

        self.add_tooltips()

    def add_tooltips(self):
        self.load_audio_btn.setToolTip("Load an audio file (WAV, MP3, etc.)")
        self.analyze_btn.setToolTip("Analyze the audio for noise profile and preview it.")
        self.denoise_btn.setToolTip("Apply AI-based noise reduction to the loaded audio.")
        self.compare_btn.setToolTip("Visualize and compare original vs. denoised waveforms.")
        self.export_btn.setToolTip("Save the cleaned audio to a WAV file.")
        self.theme_toggle_btn.setToolTip("Switch between dark and light themes.")
        self.status_log.setToolTip("Displays application messages, progress, and errors.")
        self.progress_bar.setToolTip("Shows the progress of ongoing operations.")

    def update_waveform_plot(self, original_waveform: np.ndarray, sample_rate: int, denoised_waveform: np.ndarray = None):
        self.ax.clear()
        time = np.linspace(0, len(original_waveform) / sample_rate, num=len(original_waveform))

        self.ax.plot(time, original_waveform, label="Original", color='blue', alpha=0.7)
        if denoised_waveform is not None:
            self.ax.plot(time, denoised_waveform, label="Denoised", color='red', alpha=0.7)
            self.ax.legend()

        self.ax.set_title("Waveform Comparison")
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Amplitude")
        self.ax.grid(True)
        self.fig.tight_layout()
        self.canvas.draw()

    @pyqtSlot(AudioData)
    def on_audio_loaded(self, audio_data: AudioData):
        self.current_audio_data = audio_data
        self.update_waveform_plot(audio_data.waveform, audio_data.sample_rate)
        self.analyze_btn.setEnabled(True)
        self.denoise_btn.setEnabled(True)
        self.play_original_btn.setEnabled(True)
        self.stop_playback_btn.setEnabled(True)
        self.progress_bar.setFormat("Audio Loaded")
        logger.info(f"UI: Audio loaded and displayed: {audio_data.path}")

    @pyqtSlot(DenoisingResult)
    def on_denoising_finished(self, result: DenoisingResult):
        self.denoised_audio_data = result.denoised_audio
        self.update_waveform_plot(result.original_audio.waveform, result.original_audio.sample_rate, result.denoised_audio.waveform)
        self.compare_btn.setEnabled(True)
        self.export_btn.setEnabled(True)
        self.play_denoised_btn.setEnabled(True)
        self.progress_bar.setFormat("Denoising Complete")
        logger.info("UI: Denoising finished and comparison displayed.")

    @pyqtSlot(str)
    def update_status_log(self, message: str):
        self.status_log.append(message)
        logger.info(f"Status: {message}")

    @pyqtSlot(int)
    def update_progress_bar(self, value: int):
        self.progress_bar.setValue(value)
        if value == 0:
            self.progress_bar.setFormat("Processing...")
        elif value == 100:
            self.progress_bar.setFormat("Complete")

    @pyqtSlot(str)
    def show_error_message(self, message: str):
        QMessageBox.critical(self, "Error", message)
        self.status_log.append(f"<span style='color:red;'>ERROR: {message}</span>")
        self.progress_bar.setFormat("Error")
        logger.error(f"UI Error: {message}")

    def load_audio_file(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, "Open Audio File", "", "Audio Files (*.wav *.mp3 *.flac *.ogg);;All Files (*)"
        )
        if file_path:
            self.controller.load_audio_file(file_path)

    def export_cleaned_audio(self):
        if not self.denoised_audio_data:
            self.show_error_message("No denoised audio available to export.")
            return

        file_dialog = QFileDialog()
        # Suggest a default filename based on original
        original_filename = self.current_audio_data.path.split('/')[-1].split('.')[0] if self.current_audio_data else "cleaned_audio"
        default_filename = f"{original_filename}_denoised.wav"

        output_path, _ = file_dialog.getSaveFileName(
            self, "Save Cleaned Audio", default_filename, "WAV Files (*.wav)"
        )
        if output_path:
            self.controller.export_audio(output_path)

    def compare_audio(self):
        # This button will toggle between showing original only and original vs denoised
        # For now, it just ensures the comparison plot is shown.
        if self.current_audio_data and self.denoised_audio_data:
            self.update_waveform_plot(
                self.current_audio_data.waveform,
                self.current_audio_data.sample_rate,
                self.denoised_audio_data.waveform
            )
            self.status_log.append("Displaying original vs. denoised waveforms.")
        else:
            self.status_log.append("No denoised audio to compare.")

    # --- Theme Toggling ---
    def apply_dark_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))
        self.setPalette(palette)

        # Matplotlib theme adjustment
        plt.style.use('dark_background')
        self.canvas.draw() # Redraw canvas to apply new style

    def apply_light_theme(self):
        palette = QApplication.instance().palette() # Get default light palette
        self.setPalette(palette)

        # Matplotlib theme adjustment
        plt.style.use('default') # Or 'seaborn-v0_8' etc.
        self.canvas.draw()

    def toggle_theme(self):
        current_bg_color = self.palette().color(QPalette.ColorRole.Window)
        if current_bg_color == QColor(53, 53, 53): # Check if current is dark
            self.apply_light_theme()
            logger.info("Switched to Light Theme.")
        else:
            self.apply_dark_theme()
            logger.info("Switched to Dark Theme.")

    # --- Drag and Drop ---
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.lower().endswith(('.wav', '.mp3', '.flac', '.ogg')):
                self.controller.load_audio_file(file_path)
                break # Only process the first valid audio file
        event.acceptProposedAction()
