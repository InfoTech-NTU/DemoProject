from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import QMenu, QApplication # Thêm QMenu, QApplication


class MessageBubble(QWidget):
    """Bong bóng chat hiển thị thông báo bên cạnh FloatWidget"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(layout)

        self.lbl_text = QLabel()
        self.lbl_text.setStyleSheet("""
            background-color: #1e293b;
            color: #e2e8f0;
            border: 1px solid #475569;
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 12px;
            font-weight: bold;
        """)
        self.lbl_text.setWordWrap(True)
        self.lbl_text.setMaximumWidth(200)  # Giới hạn chiều rộng để text không bị dài quá

        # Đổ bóng
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 2)
        self.lbl_text.setGraphicsEffect(shadow)

        layout.addWidget(self.lbl_text)

        # Timer tự ẩn
        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.hide)

    def show_msg(self, text, ref_pos, duration=3000):
        self.lbl_text.setText(text)
        self.adjustSize()

        # Tính vị trí: Hiển thị bên phải Widget tròn
        # ref_pos là vị trí của cục tròn
        x = ref_pos.x() + 65
        y = ref_pos.y()
        self.move(x, y)

        self.show()
        self.hide_timer.start(duration)


class FloatWidget(QWidget):
    clicked_open = Signal()  # Tín hiệu click đúp

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(60, 60)

        # Layout chính
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Vòng tròn chính
        self.circle = QLabel("🍅")
        self.circle.setAlignment(Qt.AlignCenter)
        self.circle.setFont(QFont("Segoe UI Emoji", 24))
        self.circle.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #3b82f6, stop:1 #2563eb);
                color: white;
                border-radius: 30px;
                border: 2px solid white;
            }
            QLabel:hover {
                background: #1d4ed8;
                border-color: #bfdbfe;
            }
        """)

        # Đổ bóng
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 4)
        self.circle.setGraphicsEffect(shadow)

        layout.addWidget(self.circle)

        # Init Bong bóng chat
        self.bubble = MessageBubble()

        # Biến kéo thả
        self.old_pos = None

    def update_status(self, mode="work", custom_text=None):
        """
        Cập nhật trạng thái và hiển thị thông báo.
        :param mode: 'work', 'break', 'idle'
        :param custom_text: Nội dung thông báo cụ thể (vd: 'Đóng Facebook ngay!')
        """
        if mode == "work":
            self.circle.setText("🔥")
            self.circle.setStyleSheet("""
                QLabel {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ef4444, stop:1 #dc2626);
                    color: white; border-radius: 30px; border: 2px solid #fecaca;
                }
            """)
            # Nếu có custom_text thì hiện, không thì hiện mặc định
            msg = custom_text if custom_text else "Đang tập trung!"
            self.show_bubble(msg)

        elif mode == "break":
            self.circle.setText("☕")
            self.circle.setStyleSheet("""
                QLabel {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #10b981, stop:1 #059669);
                    color: white; border-radius: 30px; border: 2px solid #a7f3d0;
                }
            """)
            msg = custom_text if custom_text else "Giờ nghỉ ngơi..."
            self.show_bubble(msg)

        else:  # Idle
            self.circle.setText("💤")
            self.circle.setStyleSheet("""
                QLabel {
                    background: #475569;
                    color: white; border-radius: 30px; border: 2px solid #94a3b8;
                }
            """)
            # Idle thường không cần hiện bong bóng trừ khi có custom_text
            if custom_text:
                self.show_bubble(custom_text)

    def show_bubble(self, text, duration=3000):
        """Hiện bong bóng chat"""
        self.bubble.show_msg(text, self.pos(), duration)

    # --- XỬ LÝ KÉO THẢ ---
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = event.globalPosition().toPoint()
            self.bubble.hide()  # Ẩn bong bóng khi kéo

    def mouseReleaseEvent(self, event):
        self.old_pos = None

    # --- XỬ LÝ CLICK ĐÚP ---
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked_open.emit()

    def closeEvent(self, event):
        self.bubble.close()
        super().closeEvent(event)

    def contextMenuEvent(self, event):
        """Bấm chuột phải vào bong bóng để hiện menu tắt"""
        menu = QMenu(self)

        # Tạo hành động Thoát
        quit_action = menu.addAction("❌ Thoát ứng dụng")

        # Hiện menu ngay tại vị trí chuột
        action = menu.exec(event.globalPos())

        if action == quit_action:
            # Gọi lệnh tắt toàn bộ app
            QApplication.instance().quit()