"""Send clearly labeled, generated images to the local assignment gallery."""

import argparse
import http.client
import io
import queue
import re
import threading
import tkinter as tk
from datetime import datetime, timezone
from pathlib import Path
from tkinter import messagebox, ttk

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
HOST = "127.0.0.1"
PORT = 8765
INTERVAL_SECONDS = 30
REQUEST_TIMEOUT_SECONDS = 5
TOKEN_PATHS = {
    "recorded": ROOT / "video-dist" / "demo-data" / ".demo-token",
    "built": ROOT / "dist" / "demo-data" / ".demo-token",
    "source": ROOT / ".demo-token",
}


def make_sample(sequence):
    """Draw the entire frame from scratch without reading the screen or files."""
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    image = Image.new("RGB", (640, 360), "#14243d")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 639, 10), fill="#59d9c1")
    draw.rounded_rectangle((25, 26, 615, 333), radius=16, fill="#1e3453")
    draw.text((51, 50), "COSC 3796   |   SIMULATION", fill="#82e7d4", font=ImageFont.load_default(18))
    draw.text((51, 104), "GENERATED TEST IMAGE", fill="white", font=ImageFont.load_default(32))
    draw.text((51, 158), f"Sample {sequence:03d}", fill="white", font=ImageFont.load_default(25))
    draw.text((51, 205), generated_at, fill="#d6e3f5", font=ImageFont.load_default(20))
    draw.text((51, 273), "This image contains no screen or personal data.", fill="#82e7d4", font=ImageFont.load_default(19))
    output = io.BytesIO()
    image.save(output, "JPEG", quality=88)
    return output.getvalue()


def upload_sample(token, sample):
    """Make one authenticated request to loopback, without proxies or redirects."""
    connection = http.client.HTTPConnection(HOST, PORT, timeout=REQUEST_TIMEOUT_SECONDS)
    try:
        connection.request(
            "POST", "/upload", body=sample,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "image/jpeg"},
        )
        with connection.getresponse() as response:
            if response.status != 201:
                raise OSError(f"Receiver returned HTTP {response.status}.")
    finally:
        connection.close()


def send_samples(token, stopped, messages):
    sequence = 1
    while not stopped.is_set():
        try:
            sample = make_sample(sequence)
            if stopped.is_set():
                break
            upload_sample(token, sample)
            messages.put(f"ON  |  Sample {sequence:03d} received. Next sample in {INTERVAL_SECONDS} seconds.")
            sequence += 1
        except (OSError, http.client.HTTPException):
            messages.put("ON  |  Delivery failed. Check that the selected local receiver is running.")
        stopped.wait(INTERVAL_SECONDS)


class SimulationWindow:
    def __init__(self, root, token_path):
        self.root = root
        self.token_path = token_path
        self.stopped = threading.Event()
        self.messages = queue.SimpleQueue()
        self.worker = None
        self.consent = tk.BooleanVar(root, value=False)
        self.status = tk.StringVar(root, value="OFF  |  Ready for explicit consent.")

        root.title("COSC 3796 | Generated image simulation")
        root.minsize(660, 295)
        panel = ttk.Frame(root, padding=24)
        panel.pack(fill="both", expand=True)
        ttk.Label(panel, text="Generated image simulation", font=("Segoe UI", 20, "bold")).pack(anchor="w")
        ttk.Label(
            panel, justify="left", wraplength=605,
            text="This separate window sends numbered test images to the local gallery every 30 seconds. "
                 "It stays open when Mario closes. The images are drawn from scratch, and the simulator never reads your screen.",
        ).pack(anchor="w", pady=(8, 15))
        self.checkbox = ttk.Checkbutton(
            panel, text="I consent to sending generated test images to http://127.0.0.1:8765/",
            variable=self.consent,
        )
        self.checkbox.pack(anchor="w")
        buttons = ttk.Frame(panel)
        buttons.pack(anchor="w", pady=12)
        self.start_button = ttk.Button(buttons, text="Start simulation", command=self.start)
        self.start_button.pack(side="left", padx=(0, 8))
        self.stop_button = ttk.Button(buttons, text="Stop simulation", command=self.stop, state="disabled")
        self.stop_button.pack(side="left")
        ttk.Label(panel, textvariable=self.status, wraplength=605).pack(anchor="w")
        root.protocol("WM_DELETE_WINDOW", self.close)
        root.after(100, self.poll)

    def start(self):
        if self.worker is not None:
            return
        if not self.consent.get():
            messagebox.showinfo("Consent required", "Tick the consent box before starting.", parent=self.root)
            return
        try:
            token = self.token_path.read_text(encoding="utf-8").strip()
            if not re.fullmatch(r"[A-Za-z0-9_-]+", token):
                raise ValueError("Invalid receiver token")
        except (OSError, ValueError):
            messagebox.showerror("Receiver not ready", "Start the selected local receiver first.", parent=self.root)
            return

        self.stopped.clear()
        self.checkbox.configure(state="disabled")
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.status.set("ON  |  Generating sample 001.")
        self.worker = threading.Thread(target=send_samples, args=(token, self.stopped, self.messages), daemon=True)
        self.worker.start()

    def stop(self):
        self.stopped.set()
        self.consent.set(False)
        self.stop_button.configure(state="disabled")
        self.status.set("STOPPING  |  A request already in progress may finish.")

    def poll(self):
        while not self.messages.empty():
            status = self.messages.get_nowait()
            if not self.stopped.is_set():
                self.status.set(status)
        if self.worker is not None and not self.worker.is_alive():
            self.worker = None
            self.checkbox.configure(state="normal")
            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
            self.status.set("OFF  |  Simulation stopped.")
        self.root.after(100, self.poll)

    def close(self):
        self.stopped.set()
        self.root.destroy()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receiver", choices=TOKEN_PATHS, default="recorded",
                        help="which local receiver's token to use (default: recorded)")
    args = parser.parse_args()
    app = tk.Tk()
    SimulationWindow(app, TOKEN_PATHS[args.receiver])
    app.mainloop()


if __name__ == "__main__":
    main()
