import tkinter as tk
from tkinter import ttk
import win32gui
import win32con
import ctypes
import sys  # 用于退出程序

def get_window_titles():
    windows = []
    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:
                windows.append((hwnd, title))
    win32gui.EnumWindows(callback, None)
    return windows

def set_window_transparency(hwnd, alpha):
    try:
        styles = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, styles | win32con.WS_EX_LAYERED)
        win32gui.SetLayeredWindowAttributes(hwnd, 0, alpha, win32con.LWA_ALPHA)
    except Exception as e:
        print("设置透明度失败:", e)

class WindowTransparencyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("窗口透明度控制器")
        self.selected_hwnd = None

        self.entry_alpha = 255  # 鼠标在窗口内时的透明度
        self.exit_alpha = 200   # 鼠标在窗口外时的透明度

        # 顶部主内容区域
        top_frame = ttk.Frame(root, padding=10)
        top_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # 左侧窗口列表
        left_frame = ttk.Frame(top_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.listbox = tk.Listbox(left_frame, width=50)
        self.listbox.pack(fill=tk.BOTH, expand=True)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)

        self.refresh_button = ttk.Button(left_frame, text="刷新窗口列表", command=self.refresh_windows)
        self.refresh_button.pack(pady=5)

        # 底部滑动条区域
        bottom_frame = ttk.Frame(root, padding=10)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # 滑动条1：鼠标在窗口内
        label1 = ttk.Label(bottom_frame, text="滑动条1: 鼠标在窗口内")
        label1.pack(anchor='w')
        self.entry_scale = ttk.Scale(bottom_frame, from_=0, to=255, orient=tk.HORIZONTAL, command=self.on_entry_scale)
        self.entry_scale.set(self.entry_alpha)
        self.entry_scale.pack(fill=tk.X, pady=5)

        # 滑动条2：鼠标在窗口外
        label2 = ttk.Label(bottom_frame, text="滑动条2: 鼠标在窗口外")
        label2.pack(anchor='w')
        self.exit_scale = ttk.Scale(bottom_frame, from_=0, to=255, orient=tk.HORIZONTAL, command=self.on_exit_scale)
        self.exit_scale.set(self.exit_alpha)
        self.exit_scale.pack(fill=tk.X, pady=5)

        self.windows = []
        self.refresh_windows()
        self.check_mouse_timer()

        # 绑定关闭窗口事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def refresh_windows(self):
        self.windows = get_window_titles()
        self.listbox.delete(0, tk.END)
        for hwnd, title in self.windows:
            self.listbox.insert(tk.END, f"{title} (hwnd={hwnd})")

    def on_select(self, event):
        selection = self.listbox.curselection()
        if selection:
            index = selection[0]
            self.selected_hwnd = self.windows[index][0]

    def on_entry_scale(self, val):
        self.entry_alpha = int(float(val))

    def on_exit_scale(self, val):
        self.exit_alpha = int(float(val))

    def is_cursor_inside_window(self, hwnd):
        try:
            rect = win32gui.GetWindowRect(hwnd)
            x, y = win32gui.GetCursorPos()
            return rect[0] <= x <= rect[2] and rect[1] <= y <= rect[3]
        except:
            return False

    def check_mouse_timer(self):
        if self.selected_hwnd:
            inside = self.is_cursor_inside_window(self.selected_hwnd)
            alpha = self.entry_alpha if inside else self.exit_alpha
            set_window_transparency(self.selected_hwnd, alpha)
        self.root.after(100, self.check_mouse_timer)

    def on_close(self):
        print("程序关闭，退出...")
        self.root.quit()  # 退出 Tkinter 主循环
        sys.exit()  # 退出 Python 程序

if __name__ == "__main__":
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    root = tk.Tk()
    app = WindowTransparencyApp(root)
    root.geometry("700x500")
    root.mainloop()
