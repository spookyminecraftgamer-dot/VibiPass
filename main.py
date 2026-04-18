"""
VibiPass - PyWebView Desktop App
Bridges browser localStorage to an encrypted JSON file on disk.
"""

import webview
import json
import os
import sys
import threading

# ── Path helpers ──────────────────────────────────────────────────────────────

def get_app_dir() -> str:
    """Return a writable directory for user data next to the app."""
    if getattr(sys, "frozen", False):
        # PyInstaller bundle
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base, "vibipass_data")
    os.makedirs(data_dir, exist_ok=True)
    return data_dir


def get_storage_path() -> str:
    return os.path.join(get_app_dir(), "store.json")


def get_html_path(page: str) -> str:
    """Return file:// URL for an HTML page."""
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS          # type: ignore[attr-defined]
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base, "html", page)
    # webview accepts plain paths; it prepends file:// internally on all OSes
    return path


# ── Persistent storage (plain JSON – crypto stays in JS/WebCrypto) ────────────

class StorageBridge:
    """Exposed to JS as `window.pywebview.api`."""

    def __init__(self):
        self._lock = threading.Lock()
        self._path = get_storage_path()
        self._data = self._load()

    # ── internal ──────────────────────────────────────────────────────────────

    def _load(self) -> dict:
        try:
            with open(self._path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save(self):
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    # ── public API (called from JS) ───────────────────────────────────────────

    def getItem(self, key: str):
        with self._lock:
            return self._data.get(key)          # None → JS null

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


# ── localStorage shim injected into every page ────────────────────────────────

LOCALSTORAGE_SHIM = """
(function () {
  if (window.__vibiStorageReady) return;
  window.__vibiStorageReady = true;

  const api = window.pywebview && window.pywebview.api;
  if (!api) { console.warn('VibiPass: pywebview API not available'); return; }

  const _cache = {};

  // Seed cache from disk synchronously before page scripts run
  // pywebview JS API calls are synchronous from the browser side
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
    key(index) {
      return Object.keys(_cache)[index] || null;
    },
    get length() {
      return Object.keys(_cache).length;
    }
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


# ── Window & navigation logic ─────────────────────────────────────────────────

_window = None


def on_loaded():
    """Inject the localStorage shim after every page navigation."""
    global _window
    if _window:
        _window.evaluate_js(LOCALSTORAGE_SHIM)


def main():
    global _window

    bridge = StorageBridge()

    # Decide start page: if profile exists on disk go straight to auth
    start_page = "auth.html" if bridge.getItem("vibipass_profile") else "landing.html"

    _window = webview.create_window(
        title="VibiPass",
        url=get_html_path(start_page),
        js_api=bridge,
        width=1024,
        height=700,
        min_size=(800, 560),
        text_select=False,
        confirm_close=False,
    )

    _window.events.loaded += on_loaded

    # Start webview (blocking)
    webview.start(debug=False)


if __name__ == "__main__":
    main()
