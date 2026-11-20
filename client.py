"""Visible screenshot sharing companion; no capture before explicit consent."""
import io
import queue
import sys
import threading
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
from urllib.request import Request, urlopen, ProxyHandler, build_opener
from PIL import ImageGrab

ROOT = (Path(sys.executable).resolve().parent.parent / 'demo-data') if getattr(sys, 'frozen', False) else Path(__file__).resolve().parent
URL = 'http://127.0.0.1:8765/upload'

class SharingWindow:
    def __init__(self, root):
        self.root = root
        self.stop_event = threading.Event()
        self.worker = None
        self.messages = queue.Queue()
        root.title('Screenshot sharing - visible consent controls')
        root.geometry('740x400')
        root.minsize(740, 400)
        tk.Label(root, text='Screen sharing companion', font=('Segoe UI', 18)).pack(pady=12)
        tk.Label(root, text='Shares your PRIMARY SCREEN with the local receiver every 30 seconds.\nClose private windows first. Images remain in captures until you delete them.\nThis window stays open when the Mario game closes.\nStop or close this window to end sharing.', justify='left').pack(padx=20)
        self.consent = tk.BooleanVar(value=False)
        self.check = tk.Checkbutton(root, text='I consent to sharing my primary screen with http://127.0.0.1:8765', variable=self.consent)
        self.check.pack(pady=12)
        self.start_button = tk.Button(root, text='Start sharing', command=self.start)
        self.start_button.pack()
        tk.Button(root, text='STOP SHARING', command=self.stop).pack(pady=5)
        self.status = tk.StringVar(value='OFF - nothing captured')
        tk.Label(root, textvariable=self.status, wraplength=620).pack()
        root.protocol('WM_DELETE_WINDOW', self.close)
        root.after(100, self.poll)

    def start(self):
        if self.worker and self.worker.is_alive():
            return
        if not self.consent.get():
            messagebox.showinfo('Consent required', 'Read the disclosure and tick the consent box before starting.')
            return
        try:
            token = (ROOT / '.demo-token').read_text(encoding='utf-8').strip()
        except OSError:
            messagebox.showerror('Receiver not ready', 'Start the screenshot receiver first.')
            return
        self.stop_event.clear()
        self.check.config(state='disabled')
        self.start_button.config(state='disabled')
        self.status.set('ON - sharing primary screen every 30 seconds')
        self.worker = threading.Thread(target=self.share, args=(token,), daemon=True)
        self.worker.start()

    def share(self, token):
        opener = build_opener(ProxyHandler({}))
        while not self.stop_event.is_set():
            try:
                shot = ImageGrab.grab(all_screens=False)
                shot.thumbnail((1600, 1000))
                buf = io.BytesIO()
                shot.convert('RGB').save(buf, 'JPEG', quality=75)
                # Stop prevents future requests; one request already in progress may finish.
                if self.stop_event.is_set():
                    break
                req = Request(URL, data=buf.getvalue(), headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'image/jpeg'}, method='POST')
                with opener.open(req, timeout=5) as response:
                    self.messages.put('ON - screenshot delivered; next capture in 30 seconds')
            except Exception as exc:
                self.messages.put('ON - delivery failed: ' + str(exc) + '; retry in 30 seconds')
            if self.stop_event.wait(30):
                break
        self.messages.put('OFF - sharing stopped')

    def stop(self):
        self.stop_event.set()
        self.status.set('Stopping - an in-flight upload may finish (up to 5 seconds)')
        self.consent.set(False)
        if not self.worker or not self.worker.is_alive():
            self.status.set('OFF - nothing captured')

    def poll(self):
        while not self.messages.empty():
            msg = self.messages.get_nowait()
            if not self.stop_event.is_set() or msg.startswith('OFF'):
                self.status.set(msg)
        if not self.worker or not self.worker.is_alive():
            self.check.config(state='normal')
            self.start_button.config(state='normal')
        self.root.after(100, self.poll)

    def close(self):
        self.stop_event.set()
        self.root.destroy()

if __name__ == '__main__':
    app = tk.Tk()
    SharingWindow(app)
    app.mainloop()
