"""
VibiPass - PyWebView Desktop App
Serves files via a local HTTP server so paths work correctly on ALL platforms.
"""
import webview
import json
import os
import sys
import threading
import http.server
import socketserver
import socket

def get_base_dir() -> str:
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

def get_app_dir() -> str:
    # Always store user data in home directory — works on all platforms
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

class SilentHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args): pass
    def log_error(self, format, *args): pass

def start_server(base_dir: str, port: int):
    os.chdir(base_dir)
    httpd = socketserver.TCPServer(('127.0.0.1', port), SilentHandler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd

class StorageBridge:
    def __init__(self):
        self._lock = threading.Lock()
        self._path = get_storage_path()
        self._data = self._load()

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
            return self._data.get(key)

    def setItem(self, key: str, value: str):
        with self._lock:
            self._data[key] = value
            self._save()
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
            return list(self._data.keys())

LOCALSTORAGE_SHIM = """
(function () {
  if (window.__vibiStorageReady) return;
  window.__vibiStorageReady = true;
  const api = window.pywebview && window.pywebview.api;
  if (!api) { console.warn('VibiPass: pywebview API not available'); return; }
  const _cache = {};
  try {
    const keys = api.getAllKeys();
    if (Array.isArray(keys)) {
      keys.forEach(k => { _cache[k] = api.getItem(k); });
    }
  } catch(e) { console.warn('VibiPass storage seed error', e); }
  const store = {
    getItem(key) {
      return Object.prototype.hasOwnProperty.call(_cache, key) ? _cache[key] : null;
    },
    setItem(key, value) {
      _cache[key] = String(value);
      api.setItem(key, String(value));
    },
    removeItem(key) {
      delete _cache[key];
      api.removeItem(key);
    },
    clear() {
      Object.keys(_cache).forEach(k => delete _cache[k]);
      api.clear();
    },
    key(index) { return Object.keys(_cache)[index] || null; },
    get length() { return Object.keys(_cache).length; }
  };
  try {
    Object.defineProperty(window, 'localStorage', {
      get() { return store; },
      configurable: true
    });
  } catch(e) {
    window.localStorage = store;
  }
})();
"""

_window = None

def on_loaded():
    global _window
    if _window:
        _window.evaluate_js(LOCALSTORAGE_SHIM)

def main():
    global _window
    bridge = StorageBridge()
    base_dir = get_base_dir()
    port = find_free_port()
    start_server(base_dir, port)
    start_page = "auth.html" if bridge.getItem("vibipass_profile") else "landing.html"
    url = f"http://127.0.0.1:{port}/html/{start_page}"
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
    _window.events.loaded += on_loaded
    webview.start(debug=False, http_server=True)

if __name__ == "__main__":
    main()
