# Example copied from https://gist.github.com/syegulalp/7cf217677e893881a18d10020f2966e4
# Adapted for Python 3.6 + 64-bit Windows

from ctypes import WINFUNCTYPE, c_int, c_uint, Structure, WinDLL, windll, sizeof, byref, pointer
from ctypes.wintypes import HWND, WPARAM, LPARAM, HANDLE, LPCWSTR, MSG
from typing import Tuple


WNDPROCTYPE = WINFUNCTYPE(c_int, HWND, c_uint, WPARAM, LPARAM)
WS_OVERLAPPEDWINDOW = 0xcf0000
SW_SHOWDEFAULT = 10
CS_CLASSDC = 0x0040
CW_USEDEFAULT = 0x80000000
WM_DESTROY = 2
WM_QUIT = 0x0012
PM_REMOVE = 0x0001


class WNDCLASSEX(Structure):
    _fields_ = [
        ("cbSize", c_uint),
        ("style", c_uint),
        ("lpfnWndProc", WNDPROCTYPE),
        ("cbClsExtra", c_int),
        ("cbWndExtra", c_int),
        ("hInstance", HANDLE),
        ("hIcon", HANDLE),
        ("hCursor", HANDLE),
        ("hbrBackground", HANDLE),
        ("lpszMenuName", LPCWSTR),
        ("lpszClassName", LPCWSTR),
        ("hIconSm", HANDLE)
    ]


user32 = WinDLL('user32', use_last_error=True)
user32.DefWindowProcW.argtypes = [HWND, c_uint, WPARAM, LPARAM]


def _window_messages_processor(hwnd, msg, w_param, l_param):
    if msg == WM_DESTROY:
        user32.PostQuitMessage(0)
        return 0

    return user32.DefWindowProcW(hwnd, msg, w_param, l_param)


def _create_hwnd_window(window_name: str, width: int, height: int) -> Tuple[int, WNDCLASSEX]:
    wnd_proc = WNDPROCTYPE(_window_messages_processor)
    h_inst = windll.kernel32.GetModuleHandleW(0)
    wclass_name = f'{window_name} Class'
    wname = window_name

    wnd_class = WNDCLASSEX()
    wnd_class.cbSize = sizeof(WNDCLASSEX)
    wnd_class.style = CS_CLASSDC
    wnd_class.lpfnWndProc = wnd_proc
    wnd_class.cbClsExtra = 0
    wnd_class.cbWndExtra = 0
    wnd_class.hInstance = h_inst
    wnd_class.hIcon = 0
    wnd_class.hCursor = 0
    wnd_class.hbrBackground = 0
    wnd_class.lpszMenuName = 0
    wnd_class.lpszClassName = wclass_name
    wnd_class.hIconSm = 0

    registering_result = windll.user32.RegisterClassExW(byref(wnd_class))
    if registering_result == 0:
        raise ValueError("Could not register window class.")

    hwnd: int = windll.user32.CreateWindowExW(
        0, wclass_name, wname,
        WS_OVERLAPPEDWINDOW,
        CW_USEDEFAULT, CW_USEDEFAULT,
        width, height, 0, 0, h_inst, 0
    )

    if not hwnd:
        raise ValueError("Could not create the window.")

    return hwnd, wnd_class


class WinAPIWindow:
    """Simple Windows API's handler class for managing a window"""

    def __init__(
        self,
        window_name: str,
        width: int,
        height: int
    ):
        hwnd, wnd_class = _create_hwnd_window(window_name, width, height)
        self.hwnd = hwnd
        self.wnd_class = wnd_class
        self.msg = MSG()

    def show(self):
        windll.user32.ShowWindow(self.hwnd, SW_SHOWDEFAULT)

    def update(self):
        windll.user32.UpdateWindow(self.hwnd)

    def process_window_messages(self) -> bool:
        if windll.user32.PeekMessageA(byref(self.msg), 0, 0, 0, PM_REMOVE):
            windll.user32.TranslateMessage(byref(self.msg))
            windll.user32.DispatchMessageA(byref(self.msg))
            return True

        return False

    @property
    def should_quit(self) -> bool:
        return self.msg.message == WM_QUIT if self.msg is not None else False


if __name__ == "__main__":
    print("WinAPI Application in python")
    window = WinAPIWindow("Test Window", 400, 200)
    window.show()
    window.update()
    while not window.should_quit:
        has_messages = window.process_window_messages()
