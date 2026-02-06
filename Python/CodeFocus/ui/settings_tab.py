from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
                               QLineEdit, QPushButton, QLabel, QComboBox, QSpinBox, QFrame,
                               QListWidgetItem, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PySide6.QtGui import QFont, QColor
from database.db_manager import (get_blacklist, add_to_blacklist, remove_from_blacklist,
                                 get_setting, update_setting)


# --- GIỮ NGUYÊN CLASS ToastNotification NHƯ CŨ ---
class ToastNotification(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.SubWindow)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.lbl_msg = QLabel()
        self.lbl_msg.setAlignment(Qt.AlignCenter)
        self.lbl_msg.setFont(QFont("Segoe UI", 10, QFont.Bold))
        # Style mặc định
        self.lbl_msg.setStyleSheet("""
            background-color: #10b981; color: white;
            border-radius: 18px; padding: 10px 20px;
        """)

        # Đổ bóng
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 4)
        self.lbl_msg.setGraphicsEffect(shadow)

        self.layout.addWidget(self.lbl_msg)

        # Animation
        self.anim = QPropertyAnimation(self, b"pos")
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        self.anim.setDuration(500)

        self.hide()

    def show_toast(self, text, type="success"):
        self.lbl_msg.setText(text)
        if type == "error":
            bg_color = "#ef4444"
        elif type == "info":
            bg_color = "#8b5cf6"
        else:
            bg_color = "#10b981"

        self.lbl_msg.setStyleSheet(f"""
            background-color: {bg_color}; color: white;
            border-radius: 18px; padding: 8px 20px; border: 1px solid rgba(255,255,255,0.2);
        """)

        self.adjustSize()
        parent = self.parent()
        if not parent: return

        target_x = (parent.width() - self.width()) // 2
        base_y = parent.height()
        target_y = base_y - self.height() - 60

        self.move(target_x, base_y)
        self.show()
        self.raise_()

        self.anim.setStartValue(QPoint(target_x, base_y))
        self.anim.setEndValue(QPoint(target_x, target_y))
        self.anim.start()

        QTimer.singleShot(2500, self.hide_toast)

    def hide_toast(self):
        start = self.pos()
        end = QPoint(start.x(), self.parent().height())
        self.anim.setStartValue(start)
        self.anim.setEndValue(end)
        self.anim.start()
        QTimer.singleShot(500, self.hide)


# --- CẬP NHẬT SETTINGS TAB ---
# --- ui/settings_tab.py ---

class SettingsTab(QWidget):
    def __init__(self, main_window_ref):
        super().__init__()
        self.main_window = main_window_ref

        # Main Layout
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)
        self.setLayout(self.layout)

        # --- PHẦN 1: CẤU HÌNH THỜI GIAN ---
        time_frame = self._create_section_frame()
        time_layout = QVBoxLayout()
        time_layout.setSpacing(15)
        time_frame.setLayout(time_layout)

        lbl_general = QLabel("⏱️ Cấu Hình Thời Gian & Hệ Thống")
        lbl_general.setFont(QFont("Segoe UI", 14, QFont.Bold))
        lbl_general.setStyleSheet("color: #f7fafc; background: transparent;")
        time_layout.addWidget(lbl_general)
        time_layout.addWidget(self._create_separator())

        # Container cho các bộ đếm (Sử dụng Grid để căn chỉnh đẹp hơn 4 mục)
        from PySide6.QtWidgets import QGridLayout  # Thêm import QGridLayout
        grid_timers = QGridLayout()
        grid_timers.setSpacing(10)

        # 1. Thời gian làm việc
        self.spin_time = self._create_spinbox(int(get_setting('pomodoro_minutes', 25)), " phút")
        grid_timers.addWidget(QLabel("🔥 Làm việc:", styleSheet="color: #e2e8f0; font-weight: bold;"), 0, 0)
        grid_timers.addWidget(self.spin_time, 0, 1)

        # 2. Thời gian nghỉ ngơi
        self.spin_break = self._create_spinbox(int(get_setting('break_minutes', 5)), " phút")
        self.spin_break.setRange(1, 60)
        grid_timers.addWidget(QLabel("☕ Nghỉ ngơi:", styleSheet="color: #e2e8f0; font-weight: bold;"), 0, 2)
        grid_timers.addWidget(self.spin_break, 0, 3)

        # 3. Thời gian ân hạn
        current_grace = int(get_setting('grace_period_seconds', 60))
        self.spin_grace = self._create_spinbox(current_grace, " giây")
        self.spin_grace.setRange(5, 300)
        grid_timers.addWidget(QLabel("⚠️ Ân hạn:", styleSheet="color: #f59e0b; font-weight: bold;"), 1, 0)
        grid_timers.addWidget(self.spin_grace, 1, 1)

        # 4. [MỚI] Thời gian ghi Log
        current_log = int(get_setting('log_interval_seconds', 30))
        self.spin_log = self._create_spinbox(current_log, " giây")
        self.spin_log.setRange(5, 300)  # Từ 5s đến 300s
        grid_timers.addWidget(QLabel("📝 Ghi log:", styleSheet="color: #60a5fa; font-weight: bold;"), 1, 2)
        grid_timers.addWidget(self.spin_log, 1, 3)

        time_layout.addLayout(grid_timers)

        # Hàng nút bấm
        btn_row = QHBoxLayout()
        btn_suggest = QPushButton("💡 Gợi ý khoa học")
        btn_suggest.clicked.connect(self.apply_science_mode)
        btn_suggest.setCursor(Qt.PointingHandCursor)
        btn_suggest.setFixedHeight(40)
        btn_suggest.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #9c27b0, stop:1 #7b1fa2);
                color: white; border-radius: 8px; font-weight: bold; padding: 0 15px;
            }
            QPushButton:hover { background: #6a1b9a; }
        """)
        btn_save = QPushButton("💾 Lưu Cấu Hình")
        btn_save.clicked.connect(self.save_all_settings)
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.setFixedHeight(40)
        btn_save.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3b82f6, stop:1 #2563eb);
                color: white; border-radius: 8px; font-weight: bold; padding: 0 15px;
            }
            QPushButton:hover { background: #1d4ed8; }
        """)
        btn_row.addWidget(btn_suggest)
        btn_row.addStretch()
        btn_row.addWidget(btn_save)
        time_layout.addLayout(btn_row)
        self.layout.addWidget(time_frame)

        # --- PHẦN 2: QUẢN LÝ BLACKLIST (Giữ nguyên) ---
        blacklist_frame = self._create_section_frame()
        blacklist_layout = QVBoxLayout()
        blacklist_layout.setSpacing(15)
        blacklist_frame.setLayout(blacklist_layout)

        lbl_black = QLabel("🛡️ Danh Sách Chặn (Blacklist)")
        lbl_black.setFont(QFont("Segoe UI", 14, QFont.Bold))
        lbl_black.setStyleSheet("color: #f7fafc; background: transparent;")
        blacklist_layout.addWidget(lbl_black)
        blacklist_layout.addWidget(self._create_separator())

        # Input Area
        input_layout = QHBoxLayout()

        self.combo_type = QComboBox()
        self.combo_type.addItems(["🌐 URL (Web)", "💻 App (Exe)"])
        self.combo_type.setFixedSize(140, 40)
        self.combo_type.setStyleSheet(self._get_input_style())

        self.txt_input = QLineEdit()
        self.txt_input.setPlaceholderText("Nhập tên (vd: facebook, game.exe)...")
        self.txt_input.setFixedHeight(40)
        self.txt_input.setStyleSheet(self._get_input_style())
        self.txt_input.returnPressed.connect(self.add_item)

        btn_add = QPushButton("➕ Thêm")
        btn_add.clicked.connect(self.add_item)
        btn_add.setCursor(Qt.PointingHandCursor)
        btn_add.setFixedSize(100, 40)
        btn_add.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #10b981, stop:1 #059669);
                color: white; border-radius: 8px; font-weight: bold;
            }
            QPushButton:hover { background: #047857; }
        """)

        input_layout.addWidget(self.combo_type)
        input_layout.addWidget(self.txt_input)
        input_layout.addWidget(btn_add)
        blacklist_layout.addLayout(input_layout)

        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget {
                background: #1a202c; color: #10b981;
                border: 2px solid #2d3748; border-radius: 8px; padding: 5px;
            }
            QListWidget::item { padding: 8px; margin: 2px; border-radius: 4px; }
            QListWidget::item:hover { background: #2d3748; }
            QListWidget::item:selected { background: #374151; color: #34d399; }
        """)
        blacklist_layout.addWidget(self.list_widget)

        btn_del = QPushButton("🗑️ Xóa mục đã chọn")
        btn_del.clicked.connect(self.delete_item)
        btn_del.setCursor(Qt.PointingHandCursor)
        btn_del.setFixedHeight(40)
        btn_del.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ef4444, stop:1 #dc2626);
                color: white; border-radius: 8px; font-weight: bold;
            }
            QPushButton:hover { background: #b91c1c; }
        """)
        blacklist_layout.addWidget(btn_del)

        self.layout.addWidget(blacklist_frame)

        # INIT TOAST
        self.toast = ToastNotification(self)
        self.load_list()

    def _create_section_frame(self):
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2d3748, stop:1 #1a202c);
                border-radius: 12px; border: 1px solid #374151;
            }
        """)
        return frame

    def _create_separator(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background: #4a5568; max-height: 1px; border: none;")
        return line

    def _create_spinbox(self, default_val, suffix):
        sb = QSpinBox()
        sb.setRange(1, 120)
        sb.setValue(default_val)
        sb.setSuffix(suffix)
        sb.setMinimumWidth(100)
        sb.setFixedHeight(40)
        sb.setStyleSheet("""
            QSpinBox {
                background: #2d3748; color: #f7fafc;
                border: 2px solid #4a5568; border-radius: 8px;
                padding: 0 10px; font-size: 11pt; font-weight: bold;
            }
            QSpinBox:focus { border-color: #3b82f6; }
        """)
        return sb

    def _get_input_style(self):
        return """
            background: #2d3748; color: #f7fafc;
            border: 2px solid #4a5568; border-radius: 8px;
            padding: 0 10px; font-size: 10pt;
        """

    def apply_science_mode(self):
        self.spin_time.setValue(25)
        self.spin_break.setValue(5)
        self.spin_grace.setValue(30)
        self.spin_log.setValue(60)  # Mặc định khoa học là 60s để đỡ nặng máy
        self.toast.show_toast("💡 Đã áp dụng: 25/5 | 30s Ân hạn | 60s Ghi log", "info")

    def save_all_settings(self):
        work_min = self.spin_time.value()
        break_min = self.spin_break.value()
        grace_sec = self.spin_grace.value()
        log_sec = self.spin_log.value()  # Lấy giá trị Log

        update_setting('pomodoro_minutes', work_min)
        update_setting('break_minutes', break_min)
        update_setting('grace_period_seconds', grace_sec)
        update_setting('log_interval_seconds', log_sec)  # Lưu vào DB

        self.main_window.refresh_settings()

        self.toast.show_toast(f"✅ Đã lưu cấu hình thành công!", "success")

    def load_list(self):
        self.list_widget.clear()
        apps, urls = get_blacklist()
        for u in urls:
            item = QListWidgetItem(f"🌐 {u}")
            item.setFont(QFont("Segoe UI", 10))
            self.list_widget.addItem(item)
        for a in apps:
            item = QListWidgetItem(f"💻 {a}")
            item.setFont(QFont("Segoe UI", 10))
            self.list_widget.addItem(item)

    def add_item(self):
        raw_text = self.txt_input.text().strip()
        if not raw_text: return

        text = raw_text.lower()
        is_app = (self.combo_type.currentIndex() == 1)

        if is_app and not text.endswith(".exe"):
            text += ".exe"

        item_type = 'app' if is_app else 'url'

        if add_to_blacklist(text, item_type):
            self.txt_input.clear()
            self.load_list()
            if hasattr(self.main_window, 'refresh_settings'):
                self.main_window.refresh_settings()

            msg = f"✅ Đã thêm: {text}"
            self.toast.show_toast(msg, "success")
            self.txt_input.setFocus()
        else:
            self.toast.show_toast("⚠️ Mục này đã tồn tại!", "error")

    def delete_item(self):
        row = self.list_widget.currentRow()
        if row < 0:
            self.toast.show_toast("⚠️ Vui lòng chọn mục để xóa", "error")
            return

        text = self.list_widget.item(row).text()
        val = text.split(" ", 1)[1]

        remove_from_blacklist(val)
        self.load_list()

        if hasattr(self.main_window, 'refresh_settings'):
            self.main_window.refresh_settings()

        self.toast.show_toast("🗑️ Đã xóa mục khỏi danh sách", "success")