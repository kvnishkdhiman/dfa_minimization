"""
DFA-Min Application Launcher.
Starts the Flask server and opens the browser.
"""

import os
import sys
import webbrowser
import threading
import time

# Ensure project root in python path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import app


def open_browser(port):
    time.sleep(1.2)
    url = f"http://127.0.0.1:{port}"
    print(f"\n[DFA-Min] Opening browser at {url} ...")
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"[DFA-Min] Could not open browser automatically: {e}")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("=" * 60)
    print(" DFA-Min: Automata Minimization & Equivalence Simulator")
    print("=" * 60)
    print(f"Server starting on http://127.0.0.1:{port}")
    print("Press Ctrl+C to stop the server.")
    print("=" * 60)

    # Launch browser thread
    threading.Thread(target=open_browser, args=(port,), daemon=True).start()

    # Run Flask server
    app.run(host="127.0.0.1", port=port, debug=False)
