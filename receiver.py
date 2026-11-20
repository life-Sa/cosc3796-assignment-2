"""Local-only authenticated screenshot receiver. Run from the project folder."""
import base64
import hmac
import io
import os
import secrets
import sys
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from PIL import Image, UnidentifiedImageError

ROOT = (Path(sys.executable).resolve().parent.parent / 'demo-data') if getattr(sys, 'frozen', False) else Path(__file__).resolve().parent
STORE = ROOT / 'captures'
LOCK = threading.Lock()
MAX_BYTES = 8 * 1024 * 1024
Image.MAX_IMAGE_PIXELS = 20_000_000

def credentials():
    ROOT.mkdir(parents=True, exist_ok=True)
    path = ROOT / '.demo-token'
    if not path.exists():
        path.write_text(secrets.token_urlsafe(32), encoding='utf-8')
    return path.read_text(encoding='utf-8').strip()

def make_handler(token):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            print(datetime.now().isoformat(timespec='seconds'), fmt % args)

        def authorized(self):
            value = self.headers.get('Authorization', '')
            basic = 'Basic ' + base64.b64encode(('demo:' + token).encode()).decode()
            return hmac.compare_digest(value, 'Bearer ' + token) or hmac.compare_digest(value, basic)

        def reply(self, status, data=b'', kind='text/plain; charset=utf-8'):
            self.send_response(status)
            self.send_header('Content-Type', kind)
            self.send_header('Content-Length', str(len(data)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Content-Security-Policy', "default-src 'none'; img-src 'self'; style-src 'unsafe-inline'")
            if status == 401:
                self.send_header('WWW-Authenticate', 'Basic realm="Local demo"')
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            if not self.authorized():
                return self.reply(401, b'Use username demo and the local demo token.')
            if self.path == '/':
                with LOCK:
                    files = sorted(STORE.glob('*.jpg'), reverse=True)
                cards = ''.join(f'<figure><img width="640" src="/images/{p.name}"><figcaption>{p.stem} UTC</figcaption></figure>' for p in files)
                page = '<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="30"><title>Consented screenshot gallery</title><style>body{font:18px system-ui;background:#eef2f7;margin:40px}img{max-width:100%;border:1px solid #aaa}figure{margin:24px 0}</style><h1>Consented screenshot gallery</h1><p>Refreshes every 30 seconds. Latest 20 captures. Local demonstration only.</p>' + (cards or '<p>No screenshots received yet.</p>')
                return self.reply(200, page.encode(), 'text/html; charset=utf-8')
            name = self.path.removeprefix('/images/')
            if self.path.startswith('/images/') and Path(name).name == name and name.endswith('.jpg'):
                with LOCK:
                    p = STORE / name
                    if p.is_file():
                        return self.reply(200, p.read_bytes(), 'image/jpeg')
            self.reply(404)

        def do_POST(self):
            if not self.authorized():
                return self.reply(401)
            if self.path != '/upload':
                return self.reply(404)
            try:
                size = int(self.headers.get('Content-Length', '0'))
                if not 0 < size <= MAX_BYTES:
                    return self.reply(413)
                self.connection.settimeout(5)
                payload = self.rfile.read(size)
                if len(payload) != size:
                    return self.reply(400)
                with Image.open(io.BytesIO(payload)) as im:
                    if im.format != 'JPEG':
                        return self.reply(415)
                    im.load()
                    out = io.BytesIO()
                    im.convert('RGB').save(out, 'JPEG', quality=80)
                with LOCK:
                    STORE.mkdir(exist_ok=True)
                    name = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%f') + '.jpg'
                    (STORE / name).write_bytes(out.getvalue())
                    for old in sorted(STORE.glob('*.jpg'), reverse=True)[20:]:
                        old.unlink()
                self.reply(201, b'Screenshot received')
            except (ValueError, OSError, UnidentifiedImageError, Image.DecompressionBombError):
                self.reply(400, b'Invalid image')
    return Handler

if __name__ == '__main__':
    token = credentials()
    print('Gallery: http://127.0.0.1:8765  Username: demo')
    print('Password/token:', token)
    print('Local access only. Ctrl+C stops receiver. Captures retained until deleted.')
    ThreadingHTTPServer(('127.0.0.1', 8765), make_handler(token)).serve_forever()
