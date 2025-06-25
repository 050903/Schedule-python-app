print('=== Bắt đầu main.py ===')
import sys
print('import sys OK')
from PyQt6.QtWidgets import QApplication
print('import QApplication OK')
from gui.main_window import MainWindow
print('import MainWindow OK')
from core.controller import ApplicationController
print('import ApplicationController OK')
from utils.logger import setup_logging
print('import setup_logging OK')
import logging
print('import logging OK')

if __name__ == "__main__":
    print("Bắt đầu setup_logging")
    setup_logging()
    print("Đã xong setup_logging")
    logger = logging.getLogger(__name__)
    logger.info("Starting AI Audio Denoising Application...")

    print("Tạo QApplication")
    app = QApplication(sys.argv)
    print("Đã tạo QApplication")

    print("Tạo ApplicationController")
    controller = ApplicationController()
    print("Đã tạo ApplicationController")

    print("Tạo MainWindow")
    main_window = MainWindow(controller)
    print("Đã tạo MainWindow")

    # Connect controller signals to main_window slots
    print("Kết nối signals/slots")
    controller.audio_loaded.connect(main_window.on_audio_loaded)
    controller.status_updated.connect(main_window.update_status_log)
    controller.progress_updated.connect(main_window.update_progress_bar)
    controller.error_occurred.connect(main_window.show_error_message)
    controller.denoising_finished.connect(main_window.on_denoising_finished)
    print("Đã kết nối signals/slots")

    print("Hiển thị main_window")
    main_window.show()
    print("Đã gọi show, bắt đầu app.exec()")
    sys.exit(app.exec())