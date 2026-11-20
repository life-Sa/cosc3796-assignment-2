"""Synthetic tests: never capture the desktop or contact external services."""
import base64
import io
import tempfile
import shutil
import threading
import unittest
from pathlib import Path
from urllib.request import Request, build_opener, ProxyHandler
from urllib.error import HTTPError
from http.server import ThreadingHTTPServer
from unittest.mock import Mock, patch
from PIL import Image
import receiver
import client

class DemoTests(unittest.TestCase):
    def test_consent_gate(self):
        ui = object.__new__(client.SharingWindow)
        ui.worker = None
        ui.consent = Mock()
        ui.consent.get.return_value = False
        with patch.object(client.messagebox, 'showinfo') as notice, patch.object(client.ImageGrab, 'grab') as grab:
            ui.start()
            notice.assert_called_once()
            grab.assert_not_called()

    def test_receiver(self):
        temp = Path(__file__).parent / 'test-captures'
        temp.mkdir(exist_ok=True)
        try:
            with patch.object(receiver, 'STORE', Path(temp)):
                server = ThreadingHTTPServer(('127.0.0.1', 0), receiver.make_handler('test-token'))
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                opener = build_opener(ProxyHandler({}))
                url = 'http://127.0.0.1:' + str(server.server_port)
                auth = {'Authorization': 'Bearer test-token'}
                def call(path, data=None, headers=auth):
                    return opener.open(Request(url + path, data=data, headers=headers), timeout=5)
                try:
                    with self.assertRaises(HTTPError) as err:
                        call('/', headers={})
                    self.assertEqual(err.exception.code, 401)
                    with self.assertRaises(HTTPError) as err:
                        call('/upload', b'not an image')
                    self.assertEqual(err.exception.code, 400)
                    image = io.BytesIO()
                    Image.new('RGB', (30, 30), 'green').save(image, 'JPEG')
                    for _ in range(22):
                        with call('/upload', image.getvalue()) as res:
                            self.assertEqual(res.status, 201)
                    self.assertEqual(len(list(Path(temp).glob('*.jpg'))), 20)
                    basic = {'Authorization': 'Basic ' + base64.b64encode(b'demo:test-token').decode()}
                    with call('/', headers=basic) as res:
                        self.assertIn(b'content="30"', res.read())
                    name = next(Path(temp).glob('*.jpg')).name
                    with call('/images/' + name) as res:
                        self.assertEqual(res.headers['Content-Type'], 'image/jpeg')
                    with self.assertRaises(HTTPError):
                        call('/images/../.demo-token')
                finally:
                    server.shutdown()
                    server.server_close()
        finally:
            shutil.rmtree(temp)

if __name__ == '__main__':
    unittest.main()
