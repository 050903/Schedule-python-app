print('Test import: bắt đầu')
try:
    from gui.main_window import MainWindow
    print('Import MainWindow OK')
except Exception as e:
    print('Import MainWindow lỗi:', e)

try:
    from core.controller import ApplicationController
    print('Import ApplicationController OK')
except Exception as e:
    print('Import ApplicationController lỗi:', e)

try:
    from utils.logger import setup_logging
    print('Import setup_logging OK')
except Exception as e:
    print('Import setup_logging lỗi:', e)

print('Test import: kết thúc') 