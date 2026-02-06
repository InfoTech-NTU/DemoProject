# Class theo dõi Window, URL, Input
import time
import psutil
import win32gui
import win32process
import uiautomation as auto
from PySide6.QtCore import QThread, Signal


class ActivityMonitor(QThread):
    # Signal gửi dữ liệu về UI: (process_name, window_title, url)
    activity_signal = Signal(str, str, str)

    def __init__(self):
        super().__init__()
        self.running = True
        self.last_window_handle = None
        self.last_url = ""

        # Danh sách các trình duyệt hỗ trợ
        self.browser_processes = ['chrome.exe', 'msedge.exe', 'brave.exe', 'firefox.exe']


    def run(self):
        """Vòng lặp vô tận của Thread"""
        while self.running:
            try:
                # 1. Lấy Active Window Handle
                hwnd = win32gui.GetForegroundWindow()

                # 2. Lấy Process Name
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                try:
                    process = psutil.Process(pid)
                    process_name = process.name().lower()
                except psutil.NoSuchProcess:
                    process_name = "unknown"

                # 3. Lấy Window Title
                window_title = win32gui.GetWindowText(hwnd)

                # 4. Lấy URL (Nếu là trình duyệt)
                url = ""
                if process_name in self.browser_processes:
                    # Chỉ quét URL nếu cửa sổ thay đổi hoặc chưa có URL
                    # Logic này giúp giảm tải CPU
                    if hwnd != self.last_window_handle or not self.last_url:
                        url = self.get_browser_url(window_title)
                        self.last_url = url
                    else:
                        url = self.last_url  # Dùng lại kết quả cũ
                else:
                    self.last_url = ""  # Reset nếu không phải trình duyệt

                self.last_window_handle = hwnd

                # 5. Gửi tín hiệu về UI
                self.activity_signal.emit(process_name, window_title, url)

            except Exception as e:
                # Bắt lỗi để thread không bị chết
                print(f"Monitor Error: {e}")

            # Nghỉ 1 giây rồi quét tiếp (đừng để thấp hơn, sẽ tốn CPU)
            self.sleep(1)

    def get_browser_url(self, window_title):
        """Dùng UI Automation để lấy URL từ thanh địa chỉ"""
        try:
            # Tìm cửa sổ trình duyệt
            window = auto.WindowControl(searchDepth=1, Name=window_title)
            if not window.Exists(0, 0):
                return ""

            # Tìm thanh địa chỉ (Address Bar)
            # Chrome/Edge thường để URL trong EditControl
            edit = window.EditControl(searchDepth=10, RegexName=".*Address.*|.*Bar.*|.*Địa chỉ.*")

            if edit.Exists(0, 0):
                # Lấy ValuePattern để đọc text
                return edit.GetValuePattern().Value
        except Exception:
            return ""
        return ""

    def stop(self):
        self.running = False
        self.wait()