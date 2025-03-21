import customtkinter as ctk
import pyautogui
import pytesseract
import numpy as np
import cv2
from PIL import Image

# SET THIS TO YOUR TESSERACT PATH
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\loush\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"

class OverlayApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # GUI Setup
        self.geometry("400x200")
        self.title("Overlay Helper")
        self.wm_attributes("-topmost", True)
        self.configure(fg_color="#1e1e1e")

        # UI Labels
        self.label = ctk.CTkLabel(self, text="Overlay is active.\nPosition me over a question.", font=("Arial", 16))
        self.label.pack(pady=20)

        self.status_label = ctk.CTkLabel(self, text="Waiting...", text_color="gray")
        self.status_label.pack(pady=10)

        # Store last detected content to avoid duplicate screenshots
        self.last_detected_text = ""
        self.last_detected_dots = 0

        # Start Scanning
        self.after(1000, self.scan_screen)

    def scan_screen(self):
        """Detects text, text boxes, and multiple-choice dots, and prevents duplicate screenshots."""
        x, y, width, height = self.winfo_x(), self.winfo_y(), self.winfo_width(), self.winfo_height()
        screenshot = pyautogui.screenshot(region=(x, y, width, height))
        screenshot_np = np.array(screenshot)
        gray = cv2.cvtColor(screenshot_np, cv2.COLOR_BGR2GRAY)

        # 🔹 1. Detect Text (Ignore Overlay Text)
        height_half = gray.shape[0] // 2
        cropped_gray = gray[height_half:, :]  # Only look at the lower part of the window

        # Use adaptive thresholding for better text contrast
        thresh = cv2.adaptiveThreshold(cropped_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY, 11, 2)
        detected_text = pytesseract.image_to_string(thresh).strip()

        # 🔹 2. Detect Multiple-Choice Dots
        blurred = cv2.GaussianBlur(gray, (11, 11), 2)
        circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1.5, minDist=15,
                                   param1=60, param2=35, minRadius=6, maxRadius=12)
        detected_dots = len(circles[0]) if circles is not None else 0

        # 🔹 3. Avoid Duplicate Screenshots
        if detected_text == self.last_detected_text and detected_dots == self.last_detected_dots:
            print("🔄 No change detected, skipping screenshot.")
            self.status_label.configure(text="No change detected.", text_color="gray")
        else:
            # Update stored values
            self.last_detected_text = detected_text
            self.last_detected_dots = detected_dots

            # Save new screenshot
            screenshot = Image.fromarray(screenshot_np)
            screenshot.save("captured_question.png")
            print(f"✅ New Screenshot saved: captured_question.png")
            print(f"📄 Detected Text: {detected_text}")
            print(f"🔘 Detected {detected_dots} multiple-choice options.")
            self.status_label.configure(text="✔️ Captured!", text_color="lightgreen")

        # Repeat scan
        self.after(1000, self.scan_screen)

# START THE APP
if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    app = OverlayApp()
    app.mainloop()
