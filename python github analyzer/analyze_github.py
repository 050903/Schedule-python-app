import os
import subprocess
import json
import logging
import shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed

import pandas as pd
import plotly.express as px
from github import Github, GithubException

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QTextEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QProgressBar, QFormLayout, QMessageBox
)
from PyQt6.QtCore import (
    QThread, QObject, pyqtSignal, Qt, QSettings, QTimer, QUrl
)
from PyQt6.QtGui import QTextCursor, QDesktopServices

# --- CẤU HÌNH VÀ HẰNG SỐ ---
APP_NAME = "GitHub Python Repo Analyzer"
ORG_NAME = "050903Org"  # Tên tổ chức/nhà phát triển cho QSettings
REPO_DIR = Path("./my_repos_optimized") # Thư mục để clone/pull repo

# Cấu hình logging để output thông tin.
# Log sẽ được gửi đến console và cũng được hiển thị trên UI.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class LogHandler(logging.Handler):
    """
    Custom logging handler để phát các log record như tín hiệu (signal)
    tới UI để hiển thị.
    """
    # message: nội dung log, level: cấp độ log (INFO, WARNING, ERROR, v.v.)
    log_signal = pyqtSignal(str, int)

    def emit(self, record):
        """Phát sinh tín hiệu với nội dung log và cấp độ."""
        msg = self.format(record)
        self.log_signal.emit(msg, record.levelno)

# Tạo một thể hiện (instance) của custom log handler
ui_log_handler = LogHandler()
# Thêm handler này vào root logger để nó bắt tất cả các log messages
logging.getLogger().addHandler(ui_log_handler)

class AnalysisWorker(QObject):
    """
    Lớp Worker thực hiện các tác vụ nặng (API call, clone, phân tích)
    trong một luồng riêng biệt để giữ cho UI phản hồi.
    """
    # Các tín hiệu (signals) để giao tiếp với luồng chính (main thread)
    progress_updated = pyqtSignal(int, str)  # current_progress, status_message
    overall_progress_range = pyqtSignal(int, int) # min_value, max_value của thanh tiến trình
    analysis_finished = pyqtSignal(pd.DataFrame) # Kết quả cuối cùng (DataFrame)
    error_occurred = pyqtSignal(str) # Thông báo lỗi
    status_message = pyqtSignal(str, int) # Thông báo trạng thái (message, level) cho log viewer trên UI

    def __init__(self, github_token: str, username: str, parent=None):
        """
        Khởi tạo AnalysisWorker.

        Args:
            github_token (str): GitHub personal access token.
            username (str): GitHub username cần phân tích.
            parent (QObject, optional): QObject cha. Mặc định là None.
        """
        super().__init__(parent)
        self._github_token = github_token
        self._username = username
        self._stop_requested = False # Cờ để yêu cầu dừng tác vụ

    def request_stop(self):
        """Yêu cầu worker dừng hoạt động một cách gracefully."""
        self._stop_requested = True
        self._log_and_emit("Analysis stop requested. Finishing current task...", logging.INFO)

    def _log_and_emit(self, message: str, level: int = logging.INFO):
        """Ghi log một message và phát nó như một tín hiệu tới UI."""
        logging.log(level, message)
        self.status_message.emit(message, level)

    def _check_dependencies(self):
        """Kiểm tra xem các công cụ dòng lệnh cần thiết đã được cài đặt chưa."""
        self._log_and_emit("Checking dependencies (git, cloc, pylint)...")
        dependencies = ["git", "cloc", "pylint"]
        for dep in dependencies:
            if not shutil.which(dep):
                raise RuntimeError(f"LỖI: Dependency '{dep}' không được tìm thấy. Vui lòng cài đặt và thử lại.")
        self._log_and_emit("✅ Tất cả dependencies đã sẵn sàng.")

    def _get_python_repos(self, github_client: Github) -> list:
        """Lấy danh sách các repo Python công khai của user bằng cách sử dụng API tìm kiếm."""
        try:
            query = f"user:{self._username} language:Python"
            self._log_and_emit(f"Đang tìm kiếm repo với query: '{query}'")
            repos = github_client.search_repositories(query)
            # Chuyển iterator thành list để lấy tổng số lượng và xử lý dễ hơn.
            # Lưu ý: GitHub API search chỉ trả về tối đa 1000 kết quả.
            repo_list = list(repos)
            self._log_and_emit(f"🔍 Tìm thấy {len(repo_list)} repo Python.")
            return repo_list
        except GithubException as e:
            raise RuntimeError(f"Lỗi khi kết nối GitHub hoặc tìm repo: {e}")
        except Exception as e:
            raise RuntimeError(f"Một lỗi không mong muốn đã xảy ra khi lấy repo: {e}")

    def _clone_or_pull_repo(self, repo) -> Path | None:
        """Clone repo nếu chưa tồn tại, hoặc pull để cập nhật nếu đã tồn tại."""
        dest_path = REPO_DIR / repo.name
        try:
            if self._stop_requested:
                self._log_and_emit(f"Bỏ qua {repo.name} do yêu cầu dừng.", logging.INFO)
                return None
            if dest_path.exists():
                self._log_and_emit(f"♻️ Đang cập nhật {repo.name}...")
                subprocess.run(
                    ["git", "pull"],
                    cwd=dest_path,
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=300 # Giới hạn thời gian (5 phút) cho các tác vụ mạng
                )
            else:
                self._log_and_emit(f"🚀 Đang clone {repo.name}...")
                subprocess.run(
                    ["git", "clone", repo.clone_url, str(dest_path)],
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=600 # Giới hạn thời gian (10 phút) cho clone ban đầu
                )
            return dest_path
        except subprocess.CalledProcessError as e:
            self._log_and_emit(f"Lỗi khi clone/pull repo {repo.name}: {e.stderr.strip()}", logging.ERROR)
            return None
        except subprocess.TimeoutExpired:
            self._log_and_emit(f"Timeout khi clone/pull cho {repo.name}", logging.ERROR)
            return None
        except Exception as e:
            self._log_and_emit(f"Lỗi không mong muốn khi clone/pull cho {repo.name}: {e}", logging.ERROR)
            return None

    def _run_cloc_analysis(self, repo_path: Path) -> dict:
        """Chạy cloc và phân tích output JSON để tăng độ tin cậy."""
        try:
            if self._stop_requested:
                return {}
            result = subprocess.run(
                ["cloc", str(repo_path), "--include-lang=Python", "--json", "--quiet"],
                capture_output=True, text=True, check=True, timeout=120 # Giới hạn 2 phút
            )
            cloc_data = json.loads(result.stdout)
            if "Python" in cloc_data:
                py_stats = cloc_data["Python"]
                return {
                    "Blank": py_stats.get("blank", 0),
                    "Comment": py_stats.get("comment", 0),
                    "Code": py_stats.get("code", 0),
                }
            return {"Blank": 0, "Comment": 0, "Code": 0} # Không tìm thấy code Python
        except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError) as e:
            self._log_and_emit(f"Cảnh báo: Không thể phân tích cloc cho {repo_path.name}: {e}", logging.WARNING)
            return {"Blank": 0, "Comment": 0, "Code": 0}
        except subprocess.TimeoutExpired:
            self._log_and_emit(f"Timeout khi phân tích cloc cho {repo_path.name}", logging.ERROR)
            return {"Blank": 0, "Comment": 0, "Code": 0}
        except Exception as e:
            self._log_and_emit(f"Lỗi không mong muốn khi phân tích cloc cho {repo_path.name}: {e}", logging.ERROR)
            return {"Blank": 0, "Comment": 0, "Code": 0}

    def _run_pylint_analysis(self, repo_path: Path) -> str:
        """
        Chạy pylint trên tất cả các file .py trong repo để có kết quả chính xác.
        Sử dụng --exit-zero để chương trình không dừng dù code có lỗi.
        Sử dụng --reports=n để chỉ lấy score.
        """
        py_files = [str(f) for f in repo_path.rglob("*.py") if f.is_file()]
        if not py_files:
            return "No Python files"

        try:
            if self._stop_requested:
                return "Stopped"
            result = subprocess.run(
                ["pylint", "--exit-zero", "--score=y", "--reports=n"] + py_files,
                capture_output=True, text=True, timeout=300 # Giới hạn 5 phút
            )
            for line in result.stdout.splitlines():
                if "Your code has been rated at" in line:
                    return line.split(" at ")[1].split(" ")[0]
            # Nếu không tìm thấy dòng chấm điểm, có thể do không có code Python hoặc lỗi khác.
            if "No files to process" in result.stdout:
                return "No Python files"
            return "Score N/A"
        except subprocess.TimeoutExpired:
            self._log_and_emit(f"Timeout khi phân tích pylint cho {repo_path.name}", logging.ERROR)
            return "Timeout"
        except Exception as e:
            self._log_and_emit(f"Lỗi khi chạy pylint cho {repo_path.name}: {e}", logging.ERROR)
            return "Analysis Error"

    def _analyze_repo(self, repo_path: Path) -> dict:
        """Hàm tổng hợp việc phân tích một repo."""
        if self._stop_requested:
            return {}
        self._log_and_emit(f"🧠 Đang phân tích {repo_path.name}...", logging.DEBUG)
        cloc_results = self._run_cloc_analysis(repo_path)
        pylint_score = self._run_pylint_analysis(repo_path)
        return {
            "Repo": repo_path.name,
            "PEP8_Score": pylint_score,
            **cloc_results
        }

    def _generate_report(self, df: pd.DataFrame):
        """Tạo file README.md và biểu đồ từ DataFrame kết quả."""
        self._log_and_emit("📊 Đang tạo báo cáo...")
        df = df.sort_values(by="Code", ascending=False).reset_index(drop=True)

        try:
            with open("README.md", "w", encoding="utf-8") as f:
                f.write(f"# 📊 Python Project Overview for {self._username}\n\n")
                f.write(f"Analyzed a total of **{len(df)}** repositories.\n\n")
                f.write("## 📄 Analysis Summary Table\n\n")
                f.write(df.to_markdown(index=False)) # Sử dụng to_markdown cho tiện lợi

            # Vẽ và lưu biểu đồ
            if not df.empty:
                fig = px.bar(
                    df.head(20),  # Chỉ hiển thị 20 repo nhiều code nhất cho dễ nhìn
                    x="Repo",
                    y="Code",
                    title=f"🔢 Dòng Code Python trong Top 20 Repo của {self._username}",
                    text="Code",
                    color="Code",
                    color_continuous_scale=px.colors.sequential.Viridis
                )
                fig.update_traces(textposition="outside")
                fig.update_layout(xaxis_title="Repo", yaxis_title="Số Dòng Code", showlegend=False)
                chart_path = "chart.png"
                fig.write_image(chart_path)
                self._log_and_emit(f"Biểu đồ đã được lưu tại {chart_path}")

                # Thêm biểu đồ vào README
                with open("README.md", "a", encoding="utf-8") as f:
                    f.write("\n\n## 📈 Biểu đồ dòng code\n\n")
                    f.write("![Biểu đồ dòng code](chart.png)\n")
            else:
                self._log_and_emit("Không có dữ liệu để tạo biểu đồ.", logging.WARNING)

            self._log_and_emit("✅ Đã tạo xong README.md và chart.png.")
        except Exception as e:
            self._log_and_emit(f"Lỗi khi tạo báo cáo: {e}", logging.ERROR)

    def run(self):
        """Hàm chính điều khiển luồng thực thi của worker."""
        try:
            self._check_dependencies()
            REPO_DIR.mkdir(exist_ok=True)

            if not self._github_token:
                raise RuntimeError("GitHub token chưa được thiết lập. Vui lòng cung cấp.")

            g = Github(self._github_token)
            repos = self._get_python_repos(g)

            if not repos:
                self._log_and_emit("Không tìm thấy repo Python nào để phân tích.", logging.WARNING)
                self.analysis_finished.emit(pd.DataFrame()) # Phát tín hiệu hoàn thành với DataFrame rỗng
                return

            # Giai đoạn 1: Clone/Pull Repositories (I/O Bound)
            self._log_and_emit("Bắt đầu clone/pull repositories...")
            cloned_paths = []
            total_repos = len(repos)
            # Thiết lập phạm vi tổng thể cho thanh tiến trình: clone + analyze
            self.overall_progress_range.emit(0, total_repos * 2)

            with ThreadPoolExecutor(max_workers=8) as executor:
                future_to_repo = {executor.submit(self._clone_or_pull_repo, repo): repo for repo in repos}
                for i, future in enumerate(as_completed(future_to_repo)):
                    if self._stop_requested:
                        raise InterruptedError("Phân tích bị dừng bởi người dùng.")
                    path = future.result()
                    if path:
                        cloned_paths.append(path)
                    # Cập nhật tiến trình cho UI (chỉ cho giai đoạn clone)
                    self.progress_updated.emit(i + 1, f"Đã clone/pull {i + 1}/{total_repos} repo...")

            if not cloned_paths:
                self._log_and_emit("Không có repository nào được clone/pull thành công.", logging.WARNING)
                self.analysis_finished.emit(pd.DataFrame())
                return

            # Giai đoạn 2: Phân tích Repositories (CPU Bound)
            self._log_and_emit("Bắt đầu phân tích repository (cloc, pylint)...")
            analysis_results = []
            total_cloned = len(cloned_paths)
            # Cập nhật điểm bắt đầu tiến trình cho giai đoạn phân tích
            self.progress_updated.emit(total_repos, "Bắt đầu phân tích...")

            with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
                future_to_path = {executor.submit(self._analyze_repo, path): path for path in cloned_paths}
                for i, future in enumerate(as_completed(future_to_path)):
                    if self._stop_requested:
                        raise InterruptedError("Phân tích bị dừng bởi người dùng.")
                    result = future.result()
                    if result:
                        analysis_results.append(result)
                    # Cập nhật tiến trình cho UI (tổng tiến trình = clone_done + analyze_progress)
                    self.progress_updated.emit(total_repos + i + 1, f"Đã phân tích {i + 1}/{total_cloned} repo...")

            if not analysis_results:
                self._log_and_emit("Không có kết quả phân tích nào được tạo.", logging.WARNING)
                self.analysis_finished.emit(pd.DataFrame())
                return

            df = pd.DataFrame(analysis_results)
            self._generate_report(df)
            self.analysis_finished.emit(df) # Phát tín hiệu với DataFrame cuối cùng
            self._log_and_emit("✅ Phân tích hoàn tất!", logging.INFO)

        except InterruptedError as ie:
            self._log_and_emit(f"Thao tác bị gián đoạn: {ie}", logging.INFO)
            self.error_occurred.emit(str(ie)) # Phát tín hiệu lỗi cho UI
            self.analysis_finished.emit(pd.DataFrame()) # Đảm bảo tín hiệu hoàn thành được phát ngay cả khi bị gián đoạn
        except RuntimeError as re:
            self._log_and_emit(f"Một lỗi nghiêm trọng đã xảy ra: {re}", logging.ERROR)
            self.error_occurred.emit(str(re))
            self.analysis_finished.emit(pd.DataFrame())
        except Exception as e:
            self._log_and_emit(f"Một lỗi không xác định đã xảy ra: {e}", logging.CRITICAL)
            self.error_occurred.emit(f"Một lỗi không mong muốn đã xảy ra: {e}")
            self.analysis_finished.emit(pd.DataFrame()) # Đảm bảo tín hiệu hoàn thành được phát để UI reset

class RepoAnalyzerApp(QMainWindow):
    """Cửa sổ ứng dụng chính cho GitHub Python Repo Analyzer."""
    def __init__(self):
        """Khởi tạo cửa sổ ứng dụng chính."""
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setGeometry(100, 100, 1000, 700) # x, y, width, height

        self._settings = QSettings(ORG_NAME, APP_NAME) # Để lưu/tải cài đặt người dùng
        self._worker_thread = None # Luồng riêng cho worker
        self._worker = None # Worker object

        self._init_ui() # Khởi tạo giao diện người dùng
        self._load_settings() # Tải cài đặt đã lưu

        # Kết nối custom log handler với log viewer của UI
        ui_log_handler.log_signal.connect(self._update_log_viewer)

    def _init_ui(self):
        """Thiết lập các phần tử giao diện người dùng và bố cục."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 1. Phần cấu hình
        config_group_layout = QFormLayout()
        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText("Nhập GitHub Personal Access Token (PAT)")
        self.token_input.setEchoMode(QLineEdit.EchoMode.Password) # Mã hóa input token
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nhập GitHub Username (ví dụ: 050903)")

        config_group_layout.addRow("GitHub Token:", self.token_input)
        config_group_layout.addRow("GitHub Username:", self.username_input)
        main_layout.addLayout(config_group_layout)

        # 2. Các nút điều khiển
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Bắt đầu Phân tích")
        self.start_button.clicked.connect(self._start_analysis)
        self.stop_button = QPushButton("Dừng Phân tích")
        self.stop_button.clicked.connect(self._stop_analysis)
        self.stop_button.setEnabled(False) # Ban đầu vô hiệu hóa
        self.view_report_button = QPushButton("Xem Báo cáo")
        self.view_report_button.clicked.connect(self._view_report)
        self.view_report_button.setEnabled(False) # Ban đầu vô hiệu hóa

        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.view_report_button)
        main_layout.addLayout(button_layout)

        # 3. Thanh tiến trình
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_status_label = QLabel("Sẵn sàng bắt đầu phân tích.")
        main_layout.addWidget(self.progress_status_label)
        main_layout.addWidget(self.progress_bar)

        # 4. Log Viewer
        main_layout.addWidget(QLabel("Nhật ký hoạt động:"))
        self.log_viewer = QTextEdit()
        self.log_viewer.setReadOnly(True)
        self.log_viewer.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap) # Không tự động xuống dòng
        main_layout.addWidget(self.log_viewer)

        # 5. Bảng kết quả
        main_layout.addWidget(QLabel("Kết quả phân tích:"))
        self.results_table = QTableWidget()
        # Đặt số cột và tiêu đề cho bảng
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels(["Repository", "PEP8 Score", "Blank Lines", "Comment Lines", "Code Lines"])
        self.results_table.horizontalHeader().setStretchLastSection(True)
        # Tự động điều chỉnh kích thước cột để lấp đầy không gian
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.results_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers) # Làm cho bảng chỉ đọc
        main_layout.addWidget(self.results_table)

    def _load_settings(self):
        """Tải cài đặt người dùng (token, username) từ QSettings."""
        token = self._settings.value("github_token", "", type=str)
        username = self._settings.value("github_username", "", type=str)

        if token:
            self.token_input.setText(token)
        else:
            # Ưu tiên biến môi trường nếu token chưa được lưu
            env_token = os.getenv("GITHUB_TOKEN")
            if env_token:
                self.token_input.setText(env_token)
                logging.info("Đã tải GitHub Token từ biến môi trường.")

        self.username_input.setText(username)

    def _save_settings(self):
        """Lưu cài đặt người dùng vào QSettings."""
        self._settings.setValue("github_token", self.token_input.text())
        self._settings.setValue("github_username", self.username_input.text())

    def _update_log_viewer(self, message: str, level: int):
        """Thêm các thông báo log vào log viewer của UI với màu sắc."""
        color = "black"
        if level >= logging.ERROR:
            color = "red"
        elif level >= logging.WARNING:
            color = "darkorange"
        elif level >= logging.INFO:
            color = "darkblue"
        elif level == logging.DEBUG:
            color = "gray"

        # Áp dụng HTML styling cho văn bản có màu
        formatted_message = f"<span style='color:{color};'>{message}</span>"
        self.log_viewer.append(formatted_message)
        # Cuộn xuống cuối
        self.log_viewer.verticalScrollBar().setValue(self.log_viewer.verticalScrollBar().maximum())

    def _start_analysis(self):
        """Khởi động quá trình phân tích trong một luồng riêng biệt."""
        token = self.token_input.text().strip()
        username = self.username_input.text().strip()

        if not token:
            QMessageBox.warning(self, "Lỗi Input", "Vui lòng cung cấp GitHub Personal Access Token.")
            return
        if not username:
            QMessageBox.warning(self, "Lỗi Input", "Vui lòng cung cấp GitHub username.")
            return

        self._save_settings() # Lưu các input hiện tại

        self._reset_ui_for_new_analysis() # Đặt lại UI cho phân tích mới

        # Tạo luồng và worker
        self._worker_thread = QThread()
        self._worker = AnalysisWorker(token, username)
        self._worker.moveToThread(self._worker_thread) # Chuyển worker đến luồng mới

        # Kết nối các tín hiệu (signals) và khe (slots)
        self._worker.progress_updated.connect(self._update_progress_bar)
        self._worker.overall_progress_range.connect(self._set_progress_bar_range)
        self._worker.analysis_finished.connect(self._handle_analysis_finished)
        self._worker.error_occurred.connect(self._handle_error)
        self._worker.status_message.connect(self._update_log_viewer)

        # Bắt đầu phương thức run của worker khi luồng bắt đầu
        self._worker_thread.started.connect(self._worker.run)
        self._worker_thread.start() # Khởi động luồng

        # Cập nhật trạng thái UI
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.view_report_button.setEnabled(False)
        self.token_input.setEnabled(False)
        self.username_input.setEnabled(False)
        self.progress_status_label.setText("Đang tiến hành phân tích...")

    def _stop_analysis(self):
        """Gửi yêu cầu dừng tới luồng worker."""
        if self._worker:
            self._worker.request_stop()
        self.stop_button.setEnabled(False) # Vô hiệu hóa nút dừng ngay lập tức
        self.progress_status_label.setText("Đang dừng phân tích...")

    def _reset_ui_for_new_analysis(self):
        """Đặt lại các phần tử UI trước khi một phân tích mới bắt đầu."""
        self.log_viewer.clear()
        self.results_table.setRowCount(0)
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(0) # Đặt lại phạm vi thanh tiến trình
        self.progress_status_label.setText("Đang khởi tạo...")
        self.view_report_button.setEnabled(False)

    def _update_progress_bar(self, value: int, status_text: str):
        """Cập nhật thanh tiến trình và nhãn trạng thái."""
        self.progress_bar.setValue(value)
        self.progress_status_label.setText(status_text)

    def _set_progress_bar_range(self, min_val: int, max_val: int):
        """Đặt phạm vi cho thanh tiến trình."""
        self.progress_bar.setRange(min_val, max_val)

    def _handle_analysis_finished(self, df: pd.DataFrame):
        """Xử lý khi phân tích hoàn tất, hiển thị kết quả."""
        if self._worker_thread and self._worker_thread.isRunning():
            self._worker_thread.quit() # Yêu cầu luồng thoát
            self._worker_thread.wait() # Đợi luồng kết thúc sạch sẽ

        self._populate_results_table(df) # Điền dữ liệu vào bảng kết quả
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.token_input.setEnabled(True)
        self.username_input.setEnabled(True)

        if not df.empty:
            self.view_report_button.setEnabled(True)
            self.progress_status_label.setText("Phân tích hoàn tất. Báo cáo đã được tạo.")
            self._log_and_emit("Phân tích đã hoàn thành và báo cáo đã được tạo thành công.", logging.INFO)
        else:
            self.progress_status_label.setText("Phân tích đã hoàn tất nhưng không có kết quả.")
            self._log_and_emit("Phân tích đã hoàn tất, nhưng không có dữ liệu nào được tạo. Kiểm tra nhật ký để biết cảnh báo/lỗi.", logging.WARNING)

        self.progress_bar.setValue(self.progress_bar.maximum()) # Đổ đầy thanh tiến trình khi hoàn tất

    def _handle_error(self, message: str):
        """Hiển thị thông báo lỗi trong QMessageBox và ghi log."""
        QMessageBox.critical(self, "Lỗi Phân tích", message)
        logging.critical(f"Lỗi UI: {message}")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.token_input.setEnabled(True)
        self.username_input.setEnabled(True)
        self.progress_status_label.setText("Phân tích thất bại.")
        self.progress_bar.setValue(0) # Đặt lại thanh tiến trình khi có lỗi

    def _populate_results_table(self, df: pd.DataFrame):
        """Điền dữ liệu từ DataFrame vào QTableWidget."""
        self.results_table.setRowCount(0) # Xóa các hàng hiện có
        if df.empty:
            logging.warning("Không có dữ liệu phân tích để hiển thị.")
            return

        # Đặt lại số cột và tiêu đề để khớp với DataFrame (đề phòng thay đổi)
        headers = ["Repo", "PEP8_Score", "Blank", "Comment", "Code"]
        self.results_table.setColumnCount(len(headers))
        self.results_table.setHorizontalHeaderLabels(["Repository", "PEP8 Score", "Blank Lines", "Comment Lines", "Code Lines"])

        self.results_table.setRowCount(len(df))
        for row_idx, (index, row_data) in enumerate(df.iterrows()):
            self.results_table.setItem(row_idx, 0, QTableWidgetItem(str(row_data["Repo"])))
            self.results_table.setItem(row_idx, 1, QTableWidgetItem(str(row_data["PEP8_Score"])))
            self.results_table.setItem(row_idx, 2, QTableWidgetItem(str(row_data["Blank"])))
            self.results_table.setItem(row_idx, 3, QTableWidgetItem(str(row_data["Comment"])))
            self.results_table.setItem(row_idx, 4, QTableWidgetItem(str(row_data["Code"])))

        self.results_table.resizeColumnsToContents() # Điều chỉnh kích thước cột theo nội dung
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch) # Đảm bảo các cột lấp đầy không gian

    def _view_report(self):
        """Mở file README.md và chart.png bằng ứng dụng mặc định của hệ thống."""
        readme_path = Path("README.md").resolve()
        chart_path = Path("chart.png").resolve()

        if readme_path.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(readme_path)))
            logging.info(f"Đã mở {readme_path}")
        else:
            logging.error("README.md không tìm thấy.")
            QMessageBox.warning(self, "Không tìm thấy Báo cáo", "README.md không tìm thấy. Vui lòng chạy phân tích trước.")

        # Mở biểu đồ sau một khoảng trễ ngắn để hệ thống có thời gian xử lý việc mở file đầu tiên
        QTimer.singleShot(500, lambda: self._open_chart(chart_path))

    def _open_chart(self, chart_path: Path):
        """Hàm trợ giúp để mở biểu đồ."""
        if chart_path.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(chart_path)))
            logging.info(f"Đã mở {chart_path}")
        else:
            logging.error("chart.png không tìm thấy.")
            QMessageBox.warning(self, "Không tìm thấy Báo cáo", "chart.png không tìm thấy. Vui lòng chạy phân tích trước.")

    def closeEvent(self, event):
        """Xử lý sự kiện đóng cửa sổ, dừng luồng worker nếu đang chạy."""
        if self._worker_thread and self._worker_thread.isRunning():
            reply = QMessageBox.question(self, 'Xác nhận thoát',
                                         "Phân tích vẫn đang chạy. Bạn có muốn dừng nó và thoát không?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self._worker.request_stop()
                self._worker_thread.quit()
                # Đợi tối đa 5 giây để luồng kết thúc sạch sẽ
                self._worker_thread.wait(5000)
                if self._worker_thread.isRunning():
                    # Nếu luồng vẫn đang chạy sau khi đợi, buộc dừng
                    self._worker_thread.terminate()
                    logging.warning("Luồng worker bị buộc dừng.")
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

if __name__ == "__main__":
    import sys

    # Tạo thư mục lưu repo nếu nó chưa tồn tại
    REPO_DIR.mkdir(parents=True, exist_ok=True)

    app = QApplication(sys.argv)
    window = RepoAnalyzerApp()
    window.show()
    sys.exit(app.exec())