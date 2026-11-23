"""Pratinjau lokal hasil build, meniru perilaku Cloudflare Pages.

Letakkan di <proyek>/tools/serve.py, lalu: python tools/serve.py [port] [bind]

Contoh: python tools/serve.py 8125            hanya 127.0.0.1
        python tools/serve.py 8125 0.0.0.0    bisa dibuka dari HP di WiFi sama

Rute yang tidak ada dibalas dist/404.html, .webp dikirim dengan content-type
yang benar, tidak ada cache, dan tidak memegang handle direktori.
"""

import os
import socket
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from io import BytesIO

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dist")
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8099
BIND = sys.argv[2] if len(sys.argv) > 2 else "127.0.0.1"


class Pratinjau(SimpleHTTPRequestHandler):
    extensions_map = {
        **SimpleHTTPRequestHandler.extensions_map,
        ".webp": "image/webp",
        ".svg": "image/svg+xml",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def send_head(self):
        if not os.path.exists(self.translate_path(self.path)):
            return self.halaman_404()
        return super().send_head()

    def halaman_404(self):
        berkas = os.path.join(ROOT, "404.html")
        if not os.path.exists(berkas):
            return super().send_head()
        with open(berkas, "rb") as f:
            isi = f.read()
        self.send_response(404)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(isi)))
        self.end_headers()
        return BytesIO(isi)


if __name__ == "__main__":
    if not os.path.isdir(ROOT):
        sys.exit("dist/ belum ada. Jalankan: python build.py")
    print("Pratinjau dist/ di http://127.0.0.1:%d" % PORT)
    if BIND != "127.0.0.1":
        try:
            ip = socket.gethostbyname(socket.gethostname())
            print("Dari perangkat lain di WiFi yang sama: http://%s:%d" % (ip, PORT))
        except OSError:
            pass
    ThreadingHTTPServer((BIND, PORT), Pratinjau).serve_forever()
