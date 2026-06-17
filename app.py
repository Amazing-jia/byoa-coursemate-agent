import cgi
import json
import re
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

VENDOR_DIR = Path(__file__).resolve().parent / ".vendor"
if VENDOR_DIR.exists():
    sys.path.insert(0, str(VENDOR_DIR))

from agent import answer_question


BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
ALLOWED_SUFFIXES = {".pptx", ".pdf", ".txt"}


def safe_filename(name):
    name = Path(name or "uploaded_material").name
    name = re.sub(r"[^A-Za-z0-9._ -]+", "_", name).strip()
    return name or "uploaded_material"


def unique_upload_path(filename):
    UPLOAD_DIR.mkdir(exist_ok=True)
    original = safe_filename(filename)
    path = UPLOAD_DIR / original
    if not path.exists():
        return path

    stem = path.stem
    suffix = path.suffix
    counter = 1
    while True:
        candidate = UPLOAD_DIR / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


class CourseMateHandler(BaseHTTPRequestHandler):
    def _send_bytes(self, status, body, content_type):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send(self, status, body, content_type="text/plain; charset=utf-8"):
        self._send_bytes(status, body.encode("utf-8"), content_type)

    def _send_json(self, status, data):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self._send_bytes(status, body, "application/json; charset=utf-8")

    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/":
            html = (BASE_DIR / "templates" / "index.html").read_text(encoding="utf-8")
            html = html.replace("{{ style_href }}", "/static/style.css")
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

        content_type = self.headers.get("Content-Type", "")
        if "multipart/form-data" in content_type:
            data = self._parse_multipart()
        else:
            data = self._parse_json()

        if isinstance(data, tuple):
            status, payload = data
            self._send_json(status, payload)
            return

        question = data["question"].strip()
        if not question:
            self._send_json(400, {"error": "请输入问题。"})
            return

        file_path = data.get("file_path")
        if not file_path:
            self._send_json(400, {"error": "请先上传一个 PPTX、PDF 或 TXT 课程资料文件。"})
            return

        api_config = {
            "api_key": data.get("api_key", ""),
            "base_url": data.get("base_url", ""),
            "model": data.get("model", ""),
        }
        use_api = data.get("use_api", "true") != "false"

        result = answer_question(
            question,
            file_path=file_path,
            use_api=use_api,
            api_config=api_config,
        )
        self._send_json(200, result)

    def _parse_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8")

        try:
            data = json.loads(raw_body or "{}")
        except json.JSONDecodeError:
            return 400, {"error": "请求格式错误。"}

        data["file_path"] = None
        return data

    def _parse_multipart(self):
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={
                "REQUEST_METHOD": "POST",
                "CONTENT_TYPE": self.headers.get("Content-Type"),
            },
        )

        data = {}
        for key in ["question", "api_key", "base_url", "model", "use_api"]:
            field = form[key] if key in form else None
            data[key] = field.value if field is not None and not field.filename else ""

        data["file_path"] = None
        upload = form["material"] if "material" in form else None
        if upload is not None and upload.filename:
            upload_name = safe_filename(upload.filename)
            suffix = Path(upload_name).suffix.lower()
            if suffix not in ALLOWED_SUFFIXES:
                return 400, {"error": "只支持上传 PPTX、PDF 或 TXT 文件。"}

            upload_path = unique_upload_path(upload_name)
            with open(upload_path, "wb") as file:
                file.write(upload.file.read())

            data["file_path"] = upload_path

        return data


def main():
    server = ThreadingHTTPServer(("127.0.0.1", 5000), CourseMateHandler)
    print("CourseMate Agent 中文网页已启动。")
    print("请在浏览器打开：http://127.0.0.1:5000")
    print("按 Ctrl+C 停止服务。")
    server.serve_forever()


if __name__ == "__main__":
    main()
