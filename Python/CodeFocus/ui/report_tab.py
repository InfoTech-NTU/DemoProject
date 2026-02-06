import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.dates as mdates
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QComboBox, QFrame, QSplitter, QTableWidget,
                               QTableWidgetItem, QHeaderView, QDateEdit)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor
import datetime

# Import DB Functions
from database.db_manager import (get_historical_data, get_daily_breakdown,
                                 get_daily_health_report, get_total_work_time_str)


class ReportTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.current_dates_map = []
        self.init_ui()

    def init_ui(self):
        # --- HEADER ---
        header = QHBoxLayout()
        title = QLabel("📊 BÁO CÁO CHI TIẾT")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #60a5fa;")
        header.addWidget(title)
        header.addStretch()

        # Date Picker
        self.date_picker = QDateEdit()
        self.date_picker.setCalendarPopup(True)
        self.date_picker.setDate(QDate.currentDate())
        self.date_picker.setDisplayFormat("dd/MM/yyyy")
        self.date_picker.dateChanged.connect(self.load_daily_detail)

        header.addWidget(QLabel("📅 Xem ngày:"))
        header.addWidget(self.date_picker)

        # Combo Filter Chart
        self.combo_chart = QComboBox()
        self.combo_chart.addItems(["7 Ngày qua", "30 Ngày qua"])
        self.combo_chart.currentIndexChanged.connect(self.load_chart_data)
        header.addWidget(self.combo_chart)
        self.layout.addLayout(header)

        # SPLITTER
        self.splitter = QSplitter(Qt.Vertical)

        # === 1. BIỂU ĐỒ ===
        self.chart_frame = QFrame()
        self.chart_frame.setStyleSheet("background: #1e293b; border-radius: 12px;")
        chart_vbox = QVBoxLayout(self.chart_frame)

        self.figure, self.ax = plt.subplots(figsize=(5, 3), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        # Bắt sự kiện click vào biểu đồ
        self.canvas.mpl_connect('button_press_event', self.on_chart_click)
        chart_vbox.addWidget(self.canvas)
        self.splitter.addWidget(self.chart_frame)

        # === 2. CHI TIẾT ===
        self.detail_container = QWidget()
        detail_layout = QVBoxLayout(self.detail_container)
        detail_layout.setContentsMargins(0, 10, 0, 0)

        # A. Tổng thời gian
        self.lbl_total_time = QLabel("⏱ Tổng thời gian: ...")
        self.lbl_total_time.setStyleSheet("font-size: 18px; font-weight: bold; color: #10b981;")
        self.lbl_total_time.setAlignment(Qt.AlignCenter)
        detail_layout.addWidget(self.lbl_total_time)

        # B. Lời khuyên
        self.advice_card = QFrame()
        self.advice_card.setStyleSheet(
            "background: #0f172a; border-radius: 8px; border-left: 5px solid #3b82f6; padding: 5px;")
        advice_layout = QVBoxLayout(self.advice_card)

        self.lbl_advice_title = QLabel("💡 LỜI KHUYÊN SỨC KHỎE:")
        self.lbl_advice_title.setStyleSheet("font-weight: bold; color: #cbd5e1;")
        self.lbl_advice_content = QLabel("...")
        self.lbl_advice_content.setWordWrap(True)
        self.lbl_advice_content.setStyleSheet("color: #94a3b8; font-style: italic;")

        advice_layout.addWidget(self.lbl_advice_title)
        advice_layout.addWidget(self.lbl_advice_content)
        detail_layout.addWidget(self.advice_card)

        # C. Bảng dữ liệu (Chia 2 cột)
        tables_layout = QHBoxLayout()

        # Cột Trái: Sessions
        col_left = QVBoxLayout()
        col_left.addWidget(QLabel("🕒 Nhật ký Phiên làm việc"))
        self.table_sessions = QTableWidget(0, 2)
        self.table_sessions.setHorizontalHeaderLabels(["Giờ", "Trạng thái"])
        self.table_sessions.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_sessions.verticalHeader().setVisible(False)
        self.table_sessions.setStyleSheet("QTableWidget { background: #0f172a; color: white; border: none; }")
        col_left.addWidget(self.table_sessions)
        tables_layout.addLayout(col_left)

        # Cột Phải: Apps/Tabs
        col_right = QVBoxLayout()
        col_right.addWidget(QLabel("💻 Chi tiết Tab & Ứng dụng"))
        self.table_apps = QTableWidget(0, 2)
        self.table_apps.setHorizontalHeaderLabels(["Nội dung", "Thời gian"])
        self.table_apps.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table_apps.setColumnWidth(1, 80)
        self.table_apps.verticalHeader().setVisible(False)
        self.table_apps.setStyleSheet("QTableWidget { background: #0f172a; color: white; border: none; }")
        col_right.addWidget(self.table_apps)
        tables_layout.addLayout(col_right)

        detail_layout.addLayout(tables_layout)
        self.splitter.addWidget(self.detail_container)
        self.layout.addWidget(self.splitter)

        self.splitter.setStretchFactor(0, 4)
        self.splitter.setStretchFactor(1, 7)

    def load_data(self):
        """Hàm này được gọi mỗi khi chuyển Tab"""
        self.load_chart_data()
        self.load_daily_detail()

    def load_chart_data(self):
        days = 7 if self.combo_chart.currentIndex() == 0 else 30
        history = get_historical_data(days)

        self.ax.clear()
        self.current_dates_map = []

        if not history:
            self.canvas.draw()
            return

        date_objs = []
        values = []

        # Chuyển đổi dict history sang list để vẽ
        sorted_keys = sorted(history.keys())  # Sắp xếp theo ngày

        for date_str in sorted_keys:
            try:
                val = history[date_str]
                d_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                date_objs.append(d_obj)
                values.append(val)
                self.current_dates_map.append(date_str)
            except ValueError:
                continue

        # Setup giao diện biểu đồ
        self.figure.patch.set_facecolor('#1e293b')
        self.ax.set_facecolor('#1e293b')

        self.ax.plot(date_objs, values, marker='o', color='#3b82f6', linewidth=2)
        self.ax.fill_between(date_objs, values, color='#3b82f6', alpha=0.15)

        myFmt = mdates.DateFormatter('%d/%m')
        self.ax.xaxis.set_major_formatter(myFmt)

        self.ax.set_ylabel("Phút", color='#94a3b8', fontsize=9)
        self.ax.tick_params(axis='x', colors='#cbd5e1', labelsize=8)
        self.ax.tick_params(axis='y', colors='#cbd5e1', labelsize=8)
        self.ax.grid(axis='y', color='#334155', linestyle='--', alpha=0.5)

        # Xóa khung
        for s in ['top', 'right']: self.ax.spines[s].set_visible(False)
        for s in ['bottom', 'left']: self.ax.spines[s].set_color('#475569')

        self.figure.tight_layout()
        self.canvas.draw()

    def on_chart_click(self, event):
        """Khi click vào điểm trên biểu đồ -> Load dữ liệu ngày đó"""
        if event.inaxes != self.ax or event.xdata is None: return
        try:
            # Tìm ngày gần nhất với điểm click
            num_dates = mdates.date2num([datetime.datetime.strptime(d, "%Y-%m-%d") for d in self.current_dates_map])
            if len(num_dates) > 0:
                closest_idx = min(range(len(num_dates)), key=lambda i: abs(num_dates[i] - event.xdata))
                date_str = self.current_dates_map[closest_idx]

                # Set lại DatePicker -> Sẽ tự trigger load_daily_detail
                q_date = QDate.fromString(date_str, "yyyy-MM-dd")
                self.date_picker.setDate(q_date)
        except Exception:
            pass

    def load_daily_detail(self):
        # 1. Lấy ngày từ Picker và CHUYỂN ĐỔI sang Python Date
        qdate = self.date_picker.date()
        # Chuyển đổi quan trọng: QDate (Qt) -> Python date object
        py_date = datetime.date(qdate.year(), qdate.month(), qdate.day())

        display_date = qdate.toString('dd/MM')

        # 2. Load Tổng quan
        time_str, total_min = get_total_work_time_str(py_date)
        self.lbl_total_time.setText(f"⏱ Ngày {display_date}: {time_str}")

        color = "#10b981"
        if total_min > 480:
            color = "#ef4444"
        elif total_min == 0:
            color = "#94a3b8"
        self.lbl_total_time.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {color}; margin-bottom: 5px;")

        # 3. Load Lời khuyên
        health_report = get_daily_health_report(py_date)
        self.lbl_advice_content.setText(health_report['advice'])
        self.advice_card.setStyleSheet(
            f"background: #0f172a; border-radius: 8px; border-left: 5px solid {health_report['color']}; padding: 10px;")

        # 4. Load Bảng chi tiết
        sessions, app_stats = get_daily_breakdown(py_date)

        # Fill bảng Sessions
        self.table_sessions.setRowCount(0)
        for s in sessions:
            row = self.table_sessions.rowCount()
            self.table_sessions.insertRow(row)

            # Giờ bắt đầu
            t_str = s.start_time.strftime('%H:%M')
            self.table_sessions.setItem(row, 0, QTableWidgetItem(t_str))

            # Trạng thái
            status_text = "Hoàn thành" if s.is_completed else "Dừng sớm"
            status_item = QTableWidgetItem(status_text)
            status_item.setForeground(QColor("#10b981" if s.is_completed else "#ef4444"))
            self.table_sessions.setItem(row, 1, status_item)

        # Fill bảng Apps
        self.table_apps.setRowCount(0)
        for app in app_stats:
            row = self.table_apps.rowCount()
            self.table_apps.insertRow(row)

            # Ưu tiên lấy Title, nếu không có thì lấy tên App
            display_name = app.window_title if app.window_title else app.process_name
            # Cắt ngắn nếu dài quá
            short_name = (display_name[:40] + '...') if len(display_name) > 40 else display_name

            item_name = QTableWidgetItem(short_name)
            item_name.setToolTip(display_name)  # Hover chuột sẽ thấy tên đầy đủ

            # Tô màu vàng nếu là web đen/game
            if app.category == "Distraction":
                item_name.setForeground(QColor("#f59e0b"))

            self.table_apps.setItem(row, 0, item_name)
            self.table_apps.setItem(row, 1, QTableWidgetItem(f"{app.count} p"))