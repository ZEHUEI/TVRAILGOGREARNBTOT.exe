import cv2
import numpy as np
import mss
import tkinter as tk
import ctypes
import os

# 1. Force a check for libraries
try:
    print("Checking libraries...")
    import keyboard

    print("Libraries OK.")
except ImportError:
    print("ERROR: Missing libraries. Run: pip install opencv-python numpy mss keyboard")
    os._exit(1)

# 2. Simplified Overlay (No transparency for testing)
root = tk.Tk()
root.title("DEBUG MODE")
root.attributes("-topmost", True)
root.geometry("200x200+100+100")  # Small window in corner

label = tk.Label(root, text="Starting...", fg="white", bg="black")
label.pack(expand=True, fill="both")

sct = mss.mss()


def update():
    try:
        # Test screen capture
        monitor = sct.monitors[1]
        region = {"top": 0, "left": 0, "width": 100, "height": 100}
        img = np.array(sct.grab(region))

        label.config(text=f"Running!\nPixels: {img.shape}", bg="green")
        print("Looping...")
    except Exception as e:
        label.config(text=f"Error:\n{e}", bg="red")
        print(f"Update Error: {e}")

    root.after(500, update)  # Run every half second


print("Starting Mainloop...")
update()
root.mainloop()