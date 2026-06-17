import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

VENDOR_DIR = Path(__file__).resolve().parent / ".vendor"
if VENDOR_DIR.exists():
    sys.path.insert(0, str(VENDOR_DIR))

from agent import DEFAULT_FILE_PATH, answer_question


BASE_DIR = Path(__file__).resolve().parent


class CourseMateHandler(BaseHTTPRequestHandler):
    def _send(self, status, body, content_type="text/plain; charset=utf-8"):
        encoded = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/":
            html = (BASE_DIR / "templates" / "index.html").read_text(encoding="utf-8")
            html = html.replace("{{ file_name }}", DEFAULT_FILE_PATH.name)
            html = html.replace("{{ url_for('static', filename='style.css') }}", "/static/style.css")
            self._send(200, html, "text/html; charset=utf-8")
            return

        if path == "/static/style.css":
            css = (BASE_DIR / "static" / "style.css").read_text(encoding="utf-8")
            self._send(200, css, "text/css; charset=utf-8")
            return

        self._send(404, "Not found")

    def do_POST(self):
        path = urlparse(self.path).path
        if path != "/ask":
            self._send(404, "Not found")
            return

        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8")

        try:
            data = json.loads(raw_body or "{}")
        except json.JSONDecodeError:
            self._send(400, json.dumps({"error": "Invalid JSON."}), "application/json")
            return

        question = (data.get("question") or "").strip()
        if not question:
            self._send(400, json.dumps({"error": "Please enter a question."}), "application/json")
            return

        result = answer_question(question)
        self._send(200, json.dumps(result), "application/json")


def main():
    server = ThreadingHTTPServer(("127.0.0.1", 5000), CourseMateHandler)
    print("CourseMate Agent web app started.")
    print("Open http://127.0.0.1:5000")
    print("Press Ctrl+C to stop.")
    server.serve_forever()


if __name__ == "__main__":
    main()
