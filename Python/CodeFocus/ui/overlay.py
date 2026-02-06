from PySide6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QPushButton,
                               QFrame, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPalette, QFont


class PenaltyOverlay(QWidget):
    unlock_signal = Signal()  # Tín hiệu mở khóa

    def __init__(self):
        super().__init__()
        # Khóa toàn màn hình, luôn nằm trên cùng
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setup_ui()

    def setup_ui(self):
        # Layout chính của toàn màn hình
        self.layout = QVBoxLayout()
        # Giảm margin bên ngoài để tránh lãng phí diện tích
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setAlignment(Qt.AlignCenter)
        self.setLayout(self.layout)

        # --- Content Container (Khung chứa nội dung chính) ---
        content_frame = QFrame()
        content_frame.setObjectName("ContentFrame")

        # Giới hạn chiều rộng nhỏ hơn để gọn gàng trên laptop
        content_frame.setFixedWidth(550)

        # Thêm hiệu ứng đổ bóng cho khung nổi bật hơn
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(50)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 10)
        content_frame.setGraphicsEffect(shadow)

        content_layout = QVBoxLayout()
        # Giảm padding bên trong khung (60 -> 40)
        content_layout.setContentsMargins(40, 40, 40, 40)
        # Giảm khoảng cách giữa các phần tử (30 -> 15)
        content_layout.setSpacing(15)
        content_layout.setAlignment(Qt.AlignCenter)
        content_frame.setLayout(content_layout)

        # 1. Icon (Giảm size 120 -> 80)
        self.lbl_icon = QLabel("🚫")
        self.lbl_icon.setFont(QFont("Segoe UI Emoji", 80))
        self.lbl_icon.setAlignment(Qt.AlignCenter)
        self.lbl_icon.setStyleSheet("background: transparent;")
        content_layout.addWidget(self.lbl_icon)

        # 2. Title
        self.lbl_title = QLabel()
        self.lbl_title.setFont(QFont("Segoe UI", 32, QFont.Bold))
        self.lbl_title.setAlignment(Qt.AlignCenter)
        self.lbl_title.setWordWrap(True)
        self.lbl_title.setStyleSheet("background: transparent;")
        content_layout.addWidget(self.lbl_title)

        # 3. Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFixedWidth(300)
        separator.setFixedHeight(2)
        separator.setStyleSheet("background: rgba(255, 255, 255, 0.3); border: none;")
        content_layout.addWidget(separator, 0, Qt.AlignCenter)

        # 4. Description
        self.lbl_desc = QLabel()
        self.lbl_desc.setFont(QFont("Segoe UI", 16))
        self.lbl_desc.setAlignment(Qt.AlignCenter)
        self.lbl_desc.setWordWrap(True)
        self.lbl_desc.setStyleSheet("background: transparent; line-height: 1.4;")  # Giảm line-height
        content_layout.addWidget(self.lbl_desc)

        # 5. Countdown
        self.lbl_countdown = QLabel()
        self.lbl_countdown.setFont(QFont("Consolas", 60, QFont.Bold))
        self.lbl_countdown.setAlignment(Qt.AlignCenter)
        self.lbl_countdown.setStyleSheet("background: transparent;")
        self.lbl_countdown.hide()
        content_layout.addWidget(self.lbl_countdown)

        # 6. Action Button
        self.btn_back = QPushButton("🔓 Tôi đã hiểu và quay lại làm việc")
        self.btn_back.setFont(QFont("Segoe UI", 14, QFont.Bold))  # Size 14
        self.btn_back.setCursor(Qt.PointingHandCursor)
        self.btn_back.setFixedSize(350, 50)  # Cố định kích thước gọn gàng (Rộng 350, Cao 50)
        self.btn_back.clicked.connect(self.request_unlock)
        self.btn_back.setObjectName("ActionButton")
        content_layout.addWidget(self.btn_back, 0, Qt.AlignCenter)

        # 7. Tip Label
        self.lbl_tip = QLabel()
        self.lbl_tip.setFont(QFont("Segoe UI", 11))
        self.lbl_tip.setAlignment(Qt.AlignCenter)
        self.lbl_tip.setWordWrap(True)
        self.lbl_tip.setStyleSheet(
            "background: transparent; color: rgba(255, 255, 255, 0.8); font-style: italic; margin-top: 10px;")
        content_layout.addWidget(self.lbl_tip)

        self.layout.addWidget(content_frame)

        # Style cho khung chứa
        content_frame.setStyleSheet("""
            QFrame#ContentFrame {
                background: rgba(20, 20, 20, 0.7); 
                border-radius: 25px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
        """)

    def set_mode(self, mode="penalty", time_left=0):
        self.setAutoFillBackground(True)
        p = self.palette()

        if mode == "penalty":
            # --- CHẾ ĐỘ PHẠT ---
            # Màu đỏ tối hơn để đỡ chói mắt ban đêm
            p.setColor(QPalette.Window, QColor(50, 0, 0))
            self.setStyleSheet("""
                QWidget {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #450a0a, stop:0.4 #7f1d1d, stop:1 #450a0a);
                }
            """)

            self.lbl_icon.setText("🚫")
            self.lbl_title.setText("CẢNH BÁO!")
            self.lbl_title.setStyleSheet("color: #fecaca; background: transparent;")

            self.lbl_desc.setText("Bạn đang mất tập trung.\nHãy quay lại công việc ngay.")
            self.lbl_desc.setStyleSheet("color: #fca5a5; background: transparent;")

            self.lbl_countdown.hide()
            self.btn_back.show()

            # Button gọn hơn
            self.btn_back.setStyleSheet("""
                QPushButton#ActionButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #3b82f6, stop:1 #2563eb);
                    color: white;
                    border: 2px solid #60a5fa;
                    border-radius: 12px;
                }
                QPushButton#ActionButton:hover {
                    background: #1d4ed8;
                    border-color: #93c5fd;
                }
                QPushButton#ActionButton:pressed {
                    background: #1e3a8a;
                    padding-top: 2px; /* Hiệu ứng nhấn */
                }
            """)

            self.lbl_tip.setText("💡 Mẹo: Kỷ luật là chìa khóa của thành công.")

        else:
            # --- CHẾ ĐỘ NGHỈ ---
            p.setColor(QPalette.Window, QColor(20, 80, 20))
            self.setStyleSheet("""
                QWidget {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #064e3b, stop:0.5 #059669, stop:1 #064e3b);
                }
            """)

            self.lbl_icon.setText("☕")
            self.lbl_title.setText("NGHỈ NGƠI")
            self.lbl_title.setStyleSheet("color: #d1fae5; background: transparent;")

            self.lbl_desc.setText("Rời mắt khỏi màn hình.\nThư giãn để nạp năng lượng.")
            self.lbl_desc.setStyleSheet("color: #a7f3d0; background: transparent;")

            self.lbl_countdown.show()
            self.update_time(time_left)
            self.btn_back.hide()

            self.lbl_tip.setText("🌿 Uống nước, vươn vai và hít thở sâu.")

        self.setPalette(p)

    def update_time(self, seconds):
        if self.lbl_countdown.isVisible():
            m, s = divmod(seconds, 60)
            self.lbl_countdown.setText(f"{m:02d}:{s:02d}")
            self.lbl_countdown.setStyleSheet("""
                color: #6ee7b7;
                background: transparent;
                font-weight: bold;
            """)

    def request_unlock(self):
        self.hide()
        self.unlock_signal.emit()