import time
import psutil
import win32gui
import win32process
import uiautomation as auto


def test_logic():
    print("--- BẮT ĐẦU TEST MONITOR ---")
    while True:
        try:
            # 1. Lấy Active Window Handle
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                print("Không tìm thấy cửa sổ active")
                time.sleep(1)
                continue

            # 2. Lấy Title
            window_title = win32gui.GetWindowText(hwnd)
            print(f"Title: {window_title}")

            # 3. Lấy Process Name
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process_name = psutil.Process(pid).name().lower()
            print(f"Process: {process_name}")

            # 4. Test lấy URL (Thử nghiệm)
            if process_name in ['chrome.exe', 'msedge.exe', 'brave.exe']:
                print(">> Đang thử quét URL (Chờ xíu)...")

                # CÁCH FIX MẠNH HƠN: Không dùng Regex Name nữa mà duyệt cây Control
                window = auto.WindowControl(searchDepth=1, Handle=hwnd)  # Dùng Handle chính xác hơn Name

                # Tìm thanh Edit (thường là thanh địa chỉ)
                # Chrome/Edge structure: Pane -> Pane -> ... -> Edit
                # Cách này tìm mọi Edit control hiển thị được
                edit = window.EditControl(searchDepth=12)

                if edit.Exists(0, 0):
                    val = edit.GetValuePattern().Value
                    print(f"✅ URL TÌM THẤY: {val}")
                else:
                    print("❌ Không tìm thấy thanh địa chỉ (UI thay đổi)")

            print("-" * 30)

        except Exception as e:
            print(f"🔥 LỖI: {e}")

        time.sleep(1.5)


if __name__ == "__main__":
    test_logic()