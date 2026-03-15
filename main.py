import cv2
import numpy as np
import mss
import tkinter as tk
import ctypes
import time
import keyboard

# Fix UI scaling issues
ctypes.windll.shcore.SetProcessDpiAwareness(1)

# --- CONFIGURATION ---
SCAN_SIZE = 20  # Increased size for a better hitbox detection around the crosshair
PIXEL_THRESHOLD = 3  # How many yellow pixels need to be seen to trigger "TRUE"
TRIGGER_KEY_CODE = 0x30
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
KEYEVENTF_SCANCODE = 0x0008
KEYEVENTF_KEYUP = 0x0002
TAP_INTERVAL = 0.1
# Standard Valorant Yellow (Deuteranopia) Enemy Highlight HSV ranges
# Note: OpenCV Hue is 0-179, Saturation 0-255, Value 0-255
LOWER_YELLOW = np.array([25, 100, 100])
UPPER_YELLOW = np.array([35, 255, 255])


# ---------------------

def click_mouse():
    """Performs a double-click on MB1"""
    # CLICK 1
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.01)
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

    time.sleep(TAP_INTERVAL)

    # CLICK 2
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.01)
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)


def press_key(hexKeyCode):
    # '0' key hardware scan code is 0x0B
    scan_code = 0x0B

    # --- TAP 1 ---
    ctypes.windll.user32.keybd_event(0, scan_code, KEYEVENTF_SCANCODE, 0)  # Down
    time.sleep(0.02)  # Micro-delay (20ms) so the game registers the press
    ctypes.windll.user32.keybd_event(0, scan_code, KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP, 0)  # Up

    # --- TAP 2 ---
    time.sleep(0.01)  # Tiny gap so the game sees two separate clicks
    ctypes.windll.user32.keybd_event(0, scan_code, KEYEVENTF_SCANCODE, 0)  # Down
    time.sleep(0.02)
    ctypes.windll.user32.keybd_event(0, scan_code, KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP, 0)  # Up


# --- OVERLAY SETUP ---
root = tk.Tk()
root.attributes("-topmost", True)
root.overrideredirect(True)
root.attributes("-transparentcolor", "black")

# Make the window click-through
root.update_idletasks()
hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
styles = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
ctypes.windll.user32.SetWindowLongW(hwnd, -20, styles | 0x80000 | 0x20)

screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()
root.geometry(f"{screen_w}x{screen_h}+0+0")

canvas = tk.Canvas(root, width=screen_w, height=screen_h, bg="black", highlightthickness=0)
canvas.pack()

# Center dot (Visual reference for scan area)
half_scan = SCAN_SIZE // 2
dot_size = 2
center_x = screen_w // 2
center_y = (screen_h // 2) - 19

# Draw a box representing the scan area instead of just a dot
scan_box = canvas.create_rectangle(
    center_x - dot_size,
    center_y - dot_size,
    center_x + dot_size,
    center_y + dot_size,
    fill="red",
)

status_text = canvas.create_text(
    screen_w - 120, 40,
    text="FALSE", fill="red", font=("Arial", 20)
)

# --- SCREEN CAPTURE LOOP ---
sct = mss.mss()
monitor = sct.monitors[1]  # Ensure this is capturing your primary monitor

region = {
    "top": center_y - half_scan,
    "left": center_x - half_scan,
    "width": SCAN_SIZE,
    "height": SCAN_SIZE
}


def update():
    if keyboard.is_pressed('f4'):  # Hold F4 to close the script
        root.destroy()
        return
    # 1. Grab screen and convert directly to HSV (mss returns BGRA)
    screen_grab = np.array(sct.grab(region))
    # Convert BGRA to BGR, then to HSV
    bgr_img = screen_grab[:, :, :3]
    hsv_img = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2HSV)

    # 2. Create a mask of pixels that fall within the yellow range
    mask = cv2.inRange(hsv_img, LOWER_YELLOW, UPPER_YELLOW)

    # 3. Count how many pixels matched the color
    matching_pixels = cv2.countNonZero(mask)

    # 4. Update UI based on threshold
    if matching_pixels >= PIXEL_THRESHOLD:
        canvas.itemconfig(status_text, text=f"TRUE ({matching_pixels})", fill="green")
        canvas.itemconfig(scan_box, outline="green")
        press_key(TRIGGER_KEY_CODE)
    else:
        canvas.itemconfig(status_text, text=f"FALSE ({matching_pixels})", fill="red")
        canvas.itemconfig(scan_box, outline="red")

    # Loop again as fast as tkinter allows (1ms delay)
    root.after(1, update)


# Start loop
update()
root.mainloop()