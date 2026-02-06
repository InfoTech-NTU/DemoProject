import os
import sys
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton,
                               QHBoxLayout, QFrame, QTabWidget, QSystemTrayIcon, QMenu)
from PySide6.QtCore import QTimer, Qt, QUrl
from PySide6.QtGui import QIcon, QAction
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput

# Import các module tự định nghĩa
from database.db_manager import (create_session, end_session, log_activity,
                                 get_blacklist, get_setting)
from core.monitor import ActivityMonitor
from ui.overlay import PenaltyOverlay
from ui.report_tab import ReportTab
from ui.settings_tab import SettingsTab
from ui.float_widget import FloatWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CodeFocus - Kỷ Luật")
        self.resize(1000, 750)

        # --- 1. QUẢN LÝ TRẠNG THÁI (STATE) ---
        self.is_running = False
        self.on_break = False
        self.is_locked = False
        self.current_session_id = None

        self.violation_counter = 0  # Đếm giây vi phạm
        self.log_counter = 0  # Đếm giây ghi log

        # Biến lưu trạng thái hoạt động gần nhất
        self.last_process = ""
        self.last_title = ""
        self.last_url = ""

        # --- 2. UI & COMPONENTS ---
        self.setup_ui()
        self.setup_float_widget()
        self.setup_system_tray()
        self.apply_styles()

        # Màn hình phạt / nghỉ ngơi
        self.overlay = PenaltyOverlay()
        self.overlay.unlock_signal.connect(self.unlock_from_penalty)

        # --- 3. LOAD CẤU HÌNH ---
        self.refresh_settings()

        # --- 4. SYSTEM (Timer & Monitor) ---
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)

        self.monitor_thread = ActivityMonitor()
        self.monitor_thread.activity_signal.connect(self.update_activity_ui)
        self.monitor_thread.start()

        # --- 5. AUDIO SETUP (MỚI THÊM) ---
        self.setup_audio()

    def setup_audio(self):
        """Cấu hình bộ phát âm thanh (Hỗ trợ chạy file .exe)"""
        self.sfx_player = QMediaPlayer()
        self.sfx_output = QAudioOutput()
        self.sfx_player.setAudioOutput(self.sfx_output)
        self.sfx_output.setVolume(1.0)

        # --- LOGIC TÌM FILE KHI CHẠY EXE ---
        # Khi đóng gói exe, dữ liệu được giải nén vào sys._MEIPASS
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
        # -----------------------------------

        self.sound_tick = os.path.join(base_path, "assets", "sounds", "tick.wav")
        self.sound_alarm = os.path.join(base_path, "assets", "sounds", "alarm.wav")

        # In ra để debug nếu cần
        print(f"Loading sound from: {self.sound_tick}")

    def play_sfx(self, file_path):
        """Hàm phát âm thanh an toàn"""
        if os.path.exists(file_path):
            self.sfx_player.setSource(QUrl.fromLocalFile(file_path))
            self.sfx_player.play()
        else:
            # Chỉ in lỗi ra console để debug, không làm crash app
            print(f"⚠️ Không tìm thấy file âm thanh: {file_path}")

    # =========================================================================
    # --- LOGIC TIMER & SESSION ---
    # =========================================================================
    def update_timer(self):
        """Hàm chạy mỗi giây"""
        self.current_time -= 1
        time_str = self.format_time(self.current_time)

        # Cập nhật Label chính
        self.lbl_timer.setText(time_str)

        # LOGIC KHI ĐANG NGHỈ (BREAK MODE)
        if self.on_break:
            # 1. Update số to trên màn hình đen (Overlay)
            self.overlay.update_time(self.current_time)

            # 2. Update bong bóng chat
            msg = f"☕ Nghỉ ngơi: {time_str}"
            self.float_widget.update_status("break", custom_text=msg)

            # 3. PHÁT TIẾNG TÍCH TẮC (5 giây cuối)
            if 0 < self.current_time <= 5:
                self.play_sfx(self.sound_tick)

        # KIỂM TRA HẾT GIỜ
        if self.current_time <= 0:
            if not self.on_break:
                self.finish_work_cycle()  # Hết giờ làm -> Sang nghỉ
            else:
                self.finish_break_cycle()  # Hết giờ nghỉ -> Báo chuông

    def start_session(self):
        self.is_running = True
        self.on_break = False
        self.current_time = self.work_duration
        self.log_counter = 0

        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.lbl_status.setText("DEEP WORK MODE")
        self.lbl_status.setStyleSheet("color: #10b981; font-weight: bold;")
        self.lbl_timer.setStyleSheet("color: #ef4444;")

        session = create_session(mode="Pomodoro")
        self.current_session_id = session.id
        self.timer.start(1000)

        self.hide()
        self.float_widget.show()
        self.float_widget.update_status("work", custom_text="Bắt đầu tập trung! Cố lên 🚀")

    def finish_work_cycle(self):
        """Kết thúc giờ làm -> Chuyển sang Nghỉ"""
        self.flush_remaining_log()
        if self.current_session_id:
            end_session(self.current_session_id, self.work_duration, is_completed=True)

        self.on_break = True
        self.current_time = self.break_duration

        # Hiện màn hình nghỉ
        self.overlay.set_mode("break", self.current_time)
        self.overlay.showFullScreen()

        self.float_widget.update_status("break", custom_text="Hết giờ! Nghỉ ngơi nào ☕")
        self.lbl_status.setText("TAKE A BREAK")
        self.lbl_status.setStyleSheet("color: #60a5fa;")
        self.lbl_timer.setStyleSheet("color: #60a5fa;")

    def finish_break_cycle(self):
        """Kết thúc giờ nghỉ -> Báo chuông & Reset"""
        # 1. PHÁT CHUÔNG BÁO HẾT GIỜ
        self.play_sfx(self.sound_alarm)

        self.on_break = False
        self.is_running = False
        self.timer.stop()
        self.overlay.hide()

        self.float_widget.update_status("idle", custom_text="Sẵn sàng phiên mới!")
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.lbl_status.setText("SẴN SÀNG")
        self.lbl_status.setStyleSheet("color: #94a3b8;")
        self.lbl_timer.setStyleSheet("color: #10b981;")

        self.refresh_settings()
        self.tab_report.load_data()
        self.show_main_from_float()
        self.tray_icon.showMessage("CodeFocus", "Đã hết giờ nghỉ! Quay lại làm việc nào.", QSystemTrayIcon.Information)

    def stop_session_manual(self):
        """Người dùng bấm nút Dừng thủ công"""
        self.timer.stop()
        self.flush_remaining_log()

        duration = self.work_duration - self.current_time
        if self.current_session_id:
            end_session(self.current_session_id, duration, is_completed=False)

        self.is_running = False
        self.on_break = False
        self.overlay.hide()
        self.float_widget.update_status("idle")

        self.refresh_settings()
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.lbl_status.setText("ĐÃ DỪNG PHIÊN")
        self.tab_report.load_data()

    # =========================================================================
    # --- LOGIC MONITOR & PENALTY (GIỮ NGUYÊN) ---
    # =========================================================================
    def flush_remaining_log(self):
        if self.is_running and self.log_counter > 0 and self.current_session_id:
            try:
                cat = "Distraction" if self.check_is_forbidden(self.last_process, self.last_title,
                                                               self.last_url) else "Work"
                log_activity(self.current_session_id, self.last_process, self.last_title, self.last_url, category=cat)
            except Exception:
                pass
            self.log_counter = 0

    def update_activity_ui(self, process, title, url):
        # 1. Cập nhật thông tin tiến trình hiện tại vào biến tạm
        self.last_process = process
        self.last_title = title
        self.last_url = url

        # 2. Hiển thị lên giao diện Dashboard (cắt ngắn nếu tên quá dài)
        display_name = title if (title and title.strip()) else process
        short_dashboard_title = (display_name[:40] + '..') if len(display_name) > 40 else display_name
        self.lbl_activity.setText(f"[{process}] {short_dashboard_title}")

        # 3. LOGIC KIỂM TRA VI PHẠM (Chỉ chạy khi đang làm việc + chưa bị khóa)
        if self.is_running and not self.on_break and not self.is_locked:
            is_bad = self.check_is_forbidden(process, title, url)

            if is_bad:
                # Nếu vi phạm -> Tăng biến đếm
                self.violation_counter += 1
                remaining = self.violation_limit - self.violation_counter

                if remaining > 0:
                    # Giai đoạn cảnh báo
                    target_name = title if (title and title.strip()) else process
                    if len(target_name) > 25: target_name = target_name[:22] + "..."

                    # Cập nhật Label chính
                    self.lbl_status.setText(f"⚠️ CẢNH BÁO: Tắt {target_name} ({remaining}s)")
                    self.lbl_status.setStyleSheet("color: #f59e0b; font-weight: bold;")

                    # Cập nhật Bong bóng (Floating Widget)
                    msg = f"⚠️ Tắt {target_name} ngay! ({remaining}s)"
                    self.float_widget.update_status("work", custom_text=msg)
                else:
                    # Hết thời gian cảnh báo -> PHẠT
                    self.trigger_penalty()
            else:
                # Nếu không vi phạm -> Reset cảnh báo nếu trước đó lỡ vi phạm
                if self.violation_counter > 0:
                    self.violation_counter = 0
                    self.lbl_status.setText("DEEP WORK MODE")
                    self.lbl_status.setStyleSheet("color: #10b981;")
                    self.float_widget.update_status("work", custom_text="Đã quay lại tập trung 👍")

        # 4. LOGIC GHI LOG (Lưu vào Database)
        if self.is_running and not self.on_break:
            self.log_counter += 1

            # --- ĐOẠN ĐÃ SỬA: Lấy thời gian từ Cài đặt ---
            # Dùng getattr để an toàn (tránh lỗi nếu chưa load settings), mặc định 30s
            limit = getattr(self, 'log_interval_limit', 30)

            if self.log_counter >= limit:
                cat = "Distraction" if self.check_is_forbidden(process, title, url) else "Work"
                log_activity(self.current_session_id, process, title, url, category=cat)
                self.log_counter = 0  # Reset đếm

    def check_is_forbidden(self, process, title, url):
        p_check = process.lower() if process else ""
        t_check = title.lower() if title else ""
        u_check = url.lower() if url else ""
        if p_check in [a.lower() for a in self.blacklist_apps]: return True
        for kw in self.blacklist_urls:
            kw = kw.lower().strip()
            if u_check and (kw in u_check): return True
            if kw in t_check: return True
            clean_kw = kw.replace("https://", "").replace("http://", "").replace("www.", "")
            domain_only = clean_kw.split('/')[0]
            if domain_only and (domain_only in t_check): return True
        return False

    def trigger_penalty(self):
        self.is_locked = True
        self.overlay.set_mode("penalty")
        self.overlay.showFullScreen()
        self.violation_counter = 0
        self.float_widget.hide()

    def unlock_from_penalty(self):
        self.is_locked = False
        self.lbl_status.setText("DEEP WORK MODE")
        if self.isHidden():
            self.float_widget.show()
            self.float_widget.update_status("work", custom_text="Đừng để xao nhãng nữa nhé!")

    # =========================================================================
    # --- SETUP UI & EVENTS ---
    # =========================================================================
    def setup_ui(self):
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.setCentralWidget(self.tabs)
        self.tab_dashboard = QWidget()
        self.setup_dashboard_tab()
        self.tab_report = ReportTab()
        self.tab_settings = SettingsTab(self)
        self.tabs.addTab(self.tab_dashboard, "🔥 Dashboard")
        self.tabs.addTab(self.tab_report, "📊 Thống kê")
        self.tabs.addTab(self.tab_settings, "⚙️ Cài đặt")
        self.tabs.currentChanged.connect(self.on_tab_change)

    def setup_dashboard_tab(self):
        layout_main = QVBoxLayout(self.tab_dashboard)
        main_container = QFrame()
        main_container.setObjectName("MainContainer")
        container_layout = QVBoxLayout(main_container)
        container_layout.setContentsMargins(40, 40, 40, 40)
        lbl_app_name = QLabel("CODE FOCUS PRO")
        lbl_app_name.setAlignment(Qt.AlignCenter)
        lbl_app_name.setStyleSheet("color: #60a5fa; font-size: 28px; font-weight: bold; margin-bottom: 20px;")
        container_layout.addWidget(lbl_app_name)
        timer_frame = QFrame()
        timer_frame.setObjectName("TimerFrame")
        timer_frame.setFixedSize(300, 300)
        timer_layout = QVBoxLayout(timer_frame)
        self.lbl_timer = QLabel("00:00")
        self.lbl_timer.setObjectName("TimerLabel")
        self.lbl_timer.setAlignment(Qt.AlignCenter)
        self.lbl_status = QLabel("Ready to Focus")
        self.lbl_status.setObjectName("StatusLabel")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        self.lbl_status.setWordWrap(True)
        timer_layout.addStretch()
        timer_layout.addWidget(self.lbl_timer)
        timer_layout.addWidget(self.lbl_status)
        timer_layout.addStretch()
        container_layout.addWidget(timer_frame, 0, Qt.AlignCenter)
        activity_frame = QFrame()
        activity_frame.setObjectName("ActivityFrame")
        activity_layout = QVBoxLayout(activity_frame)
        self.lbl_activity = QLabel("Waiting for activity...")
        self.lbl_activity.setAlignment(Qt.AlignCenter)
        activity_layout.addWidget(self.lbl_activity)
        container_layout.addWidget(activity_frame)
        btn_layout = QHBoxLayout()
        self.btn_start = QPushButton("▶ BẮT ĐẦU PHIÊN")
        self.btn_start.setObjectName("StartButton")
        self.btn_start.setCursor(Qt.PointingHandCursor)
        self.btn_start.clicked.connect(self.start_session)
        self.btn_stop = QPushButton("⏹ KẾT THÚC")
        self.btn_stop.setObjectName("StopButton")
        self.btn_stop.setCursor(Qt.PointingHandCursor)
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self.stop_session_manual)
        btn_layout.addWidget(self.btn_start)
        btn_layout.addWidget(self.btn_stop)
        container_layout.addLayout(btn_layout)
        layout_main.addWidget(main_container)

    def setup_float_widget(self):
        self.float_widget = FloatWidget()
        self.float_widget.clicked_open.connect(self.show_main_from_float)
        screen_geo = self.screen().availableGeometry()
        self.float_widget.move(screen_geo.width() - 120, screen_geo.height() - 150)

    def setup_system_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        try:
            self.tray_icon.setIcon(QIcon("assets/icon.ico"))
        except:
            pass
        tray_menu = QMenu()
        action_show = QAction("Mở giao diện", self)
        action_show.triggered.connect(self.show_main_from_float)
        action_quit = QAction("Thoát hoàn toàn", self)
        action_quit.triggered.connect(self.quit_app)
        tray_menu.addAction(action_show)
        tray_menu.addSeparator()
        tray_menu.addAction(action_quit)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick: self.show_main_from_float()

    def refresh_settings(self):
        self.blacklist_apps, self.blacklist_urls = get_blacklist()
        if not self.is_running:
            self.work_duration = int(get_setting('pomodoro_minutes', 25)) * 60
            self.break_duration = int(get_setting('break_minutes', 5)) * 60
            self.violation_limit = int(get_setting('grace_period_seconds', 60))

            self.log_interval_limit = int(get_setting('log_interval_seconds', 30))

            self.current_time = self.work_duration
            if hasattr(self, 'lbl_timer'):
                self.lbl_timer.setText(self.format_time(self.work_duration))

    def on_tab_change(self, index):
        if index == 1: self.tab_report.load_data()

    def format_time(self, seconds):
        mins, secs = divmod(seconds, 60)
        return f"{mins:02d}:{secs:02d}"

    def show_main_from_float(self):
        self.showNormal()
        self.activateWindow()
        self.float_widget.hide()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.float_widget.show()
        self.tray_icon.showMessage("CodeFocus", "Ứng dụng đã thu nhỏ xuống khay hệ thống.", QSystemTrayIcon.Information,
                                   2000)

    def quit_app(self):
        self.flush_remaining_log()
        if self.monitor_thread.isRunning(): self.monitor_thread.terminate()
        self.float_widget.close()
        self.overlay.close()
        self.close()
        sys.exit(0)

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #0f172a; }
            QFrame#MainContainer { background-color: #1e293b; border-radius: 20px; border: 1px solid #334155;}
            QFrame#TimerFrame { background-color: #0f172a; border: 6px solid #3b82f6; border-radius: 150px; }
            QLabel#TimerLabel { color: #e2e8f0; font-size: 72px; font-weight: bold; font-family: 'Consolas'; }
            QFrame#ActivityFrame { background-color: #0f172a; border-radius: 10px; padding: 10px; border: 1px solid #334155;}
            QLabel { color: #94a3b8; font-size: 14px; }
            QPushButton { height: 50px; border-radius: 10px; font-weight: bold; font-size: 14px;}
            QPushButton#StartButton { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #10b981, stop:1 #059669); color: white; border: none;}
            QPushButton#StartButton:hover { background: #047857; }
            QPushButton#StopButton { background: #ef4444; color: white; border: none;}
            QPushButton#StopButton:hover { background: #dc2626; }
            QPushButton:disabled { background-color: #334155; color: #64748b; }
        """)