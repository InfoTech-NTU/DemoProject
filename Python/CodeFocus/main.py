import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from ui.main_window import MainWindow
from database.db_manager import initialize_db, seed_sample_data


def main():
    # 1. Khởi tạo Database
    # Kiểm tra và tạo bảng nếu chưa có
    initialize_db()
    seed_sample_data()
    # (Tùy chọn) Thêm dữ liệu mẫu nếu DB trống để test

    # 2. Khởi tạo App
    app = QApplication(sys.argv)

    # Thiết lập thông tin chung cho App
    app.setApplicationName("CodeFocus")
    app.setApplicationDisplayName("CodeFocus - Focus & Health")

    # Set icon cho App (Sẽ hiển thị trên thanh Taskbar và Title bar)ó
    try:
        app.setWindowIcon(QIcon("assets/icon.ico"))
    except:
        pass  # Bỏ qua nếu chưa có file icon

    # Áp dụng Style Fusion cho giao diện đẹp và đồng bộ hơn trên các OS
    app.setStyle("Fusion")

    # 3. Hiển thị giao diện chính
    window = MainWindow()
    window.show()

    # 4. Chạy vòng lặp sự kiện
    sys.exit(app.exec())


if __name__ == "__main__":
    main()