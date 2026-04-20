"""
VibiPass - PyWebView Desktop App
Injects localStorage shim directly into HTML before serving.
"""

import webview
import json
import os
import sys
import threading
import socketserver
import socket
from http.server import SimpleHTTPRequestHandler
from io import BytesIO


def get_base_dir() -> str:
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


def get_app_dir() -> str:
    if sys.platform == "win32":
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
    elif sys.platform == "darwin":
        base = os.path.expanduser("~/Library/Application Support")
    else:
        base = os.path.expanduser("~/.local/share")
    data_dir = os.path.join(base, "VibiPass")
    os.makedirs(data_dir, exist_ok=True)
    return data_dir


def get_storage_path() -> str:
    return os.path.join(get_app_dir(), "store.json")


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


class StorageBridge:
    def __init__(self):
        self._lock = threading.Lock()
        self._path = get_storage_path()
        self._data = self._load()
        print(f"[VibiPass] Storage path: {self._path}")
        print(f"[VibiPass] Existing keys: {list(self._data.keys())}")

    def _load(self) -> dict:
        try:
            with open(self._path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save(self):
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    def getItem(self, key: str):
        with self._lock:
            val = self._data.get(key)
            print(f"[VibiPass] getItem({key}) = {str(val)[:50] if val else None}")
            return val

    def setItem(self, key: str, value: str):
        with self._lock:
            self._data[key] = value
            self._save()
            print(f"[VibiPass] setItem({key}) saved ✅")
        return True

    def removeItem(self, key: str):
        with self._lock:
            self._data.pop(key, None)
            self._save()
        return True

    def clear(self):
        with self._lock:
            self._data.clear()
            self._save()
        return True

    def getAllKeys(self):
        with self._lock:
            keys = list(self._data.keys())
            print(f"[VibiPass] getAllKeys() = {keys}")
            return keys


# This shim is injected directly into the HTML before any page script runs
SHIM_SCRIPT = """<script>
(function () {
  // Poll until pywebview API is ready, then install shim
  function installShim() {
    var api = window.pywebview && window.pywebview.api;
    if (!api) { setTimeout(installShim, 50); return; }
    if (window.__vibiStorageReady) return;
    window.__vibiStorageReady = true;

    var _cache = {};
    try {
      var keys = api.getAllKeys();
      if (Array.isArray(keys)) {
        keys.forEach(function(k) { _cache[k] = api.getItem(k); });
      }
    } catch(e) {}

    var store = {
      getItem: function(key) {
        return Object.prototype.hasOwnProperty.call(_cache, key) ? _cache[key] : null;
      },
      setItem: function(key, value) {
        _cache[key] = String(value);
        try { api.setItem(key, String(value)); } catch(e) {}
      },
      removeItem: function(key) {
        delete _cache[key];
        try { api.removeItem(key); } catch(e) {}
      },
      clear: function() {
        Object.keys(_cache).forEach(function(k) { delete _cache[k]; });
        try { api.clear(); } catch(e) {}
      },
      key: function(index) { return Object.keys(_cache)[index] || null; },
      get length() { return Object.keys(_cache).length; }
    };

    try {
      Object.defineProperty(window, 'localStorage', {
        get: function() { return store; },
        configurable: true
      });
    } catch(e) { window.localStorage = store; }

    console.log('[VibiPass] localStorage shim ready ✅', Object.keys(_cache));
  }
  installShim();
})();
</script>"""


def make_handler(base_dir):
    class ShimInjectingHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=base_dir, **kwargs)

        def log_message(self, format, *args): pass
        def log_error(self, format, *args): pass

        def do_GET(self):
            # Only inject into HTML files
            if self.path.endswith('.html') or '?' not in self.path and self.path.split('.')[-1] in ('html',):
                try:
                    # Build file path
                    clean_path = self.path.split('?')[0].lstrip('/')
                    file_path = os.path.join(base_dir, clean_path)

                    if os.path.isfile(file_path):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()

                        # Inject shim right after <head> tag
                        if '<head>' in content:
                            content = content.replace('<head>', '<head>' + SHIM_SCRIPT, 1)
                        elif '<HEAD>' in content:
                            content = content.replace('<HEAD>', '<HEAD>' + SHIM_SCRIPT, 1)
                        else:
                            content = SHIM_SCRIPT + content

                        encoded = content.encode('utf-8')
                        self.send_response(200)
                        self.send_header('Content-Type', 'text/html; charset=utf-8')
                        self.send_header('Content-Length', str(len(encoded)))
                        self.end_headers()
                        self.wfile.write(encoded)
                        return
                except Exception as e:
                    print(f"[VibiPass] Shim inject error: {e}")

            # Fall back to normal file serving
            super().do_GET()

    return ShimInjectingHandler


def start_server(base_dir: str, port: int):
    handler = make_handler(base_dir)
    httpd = socketserver.TCPServer(('127.0.0.1', port), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


_window = None


def main():
    global _window

    bridge = StorageBridge()
    base_dir = get_base_dir()

    port = find_free_port()
    start_server(base_dir, port)

    start_page = "auth.html" if bridge.getItem("vibipass_profile") else "landing.html"
    url = f"http://127.0.0.1:{port}/html/{start_page}"
    print(f"[VibiPass] Starting on: {url}")

    _window = webview.create_window(
        title="VibiPass",
        url=url,
        js_api=bridge,
        width=1024,
        height=700,
        min_size=(800, 560),
        text_select=False,
        confirm_close=False,
    )

    webview.start(debug=False)


if __name__ == "__main__":
    main()
