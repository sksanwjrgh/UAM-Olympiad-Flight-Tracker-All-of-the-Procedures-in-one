#!/usr/bin/env python3
"""RKSI · RKSS 통합 HTML용 최소 OpenSky 로컬 프록시.

127.0.0.1에만 바인딩하며, 허용된 OpenSky 인증/항적 엔드포인트만 중계한다.
자격증명과 토큰은 파일이나 로그에 기록하지 않는다.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import threading
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parent
HOST = "127.0.0.1"
DEFAULT_PORT = 8765
API_BASE = os.environ.get("OPENSKY_API_BASE", "https://opensky-network.org").rstrip("/")
AUTH_URL = os.environ.get(
    "OPENSKY_AUTH_URL",
    "https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token",
)
STATE_PARAMS = {"lamin", "lomin", "lamax", "lomax", "time", "icao24", "extended"}
FORWARD_HEADERS = {
    "content-type",
    "x-rate-limit-remaining",
    "x-rate-limit-retry-after-seconds",
}


class OpenSkyHandler(SimpleHTTPRequestHandler):
    server_version = "RKSI-RKSS-OpenSky-Proxy/1.0"

    def log_message(self, fmt: str, *args: object) -> None:
        # 요청 본문·Authorization 헤더는 출력하지 않는다.
        sys.stdout.write("[%s] %s\n" % (self.log_date_time_string(), fmt % args))

    def end_headers(self) -> None:
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        super().end_headers()

    def _json_error(self, status: int, message: str) -> None:
        body = json.dumps({"error": message}, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _relay(self, request: urllib.request.Request) -> None:
        try:
            with urllib.request.urlopen(request, timeout=25) as response:
                body = response.read()
                self.send_response(response.status)
                for name, value in response.headers.items():
                    if name.lower() in FORWARD_HEADERS:
                        self.send_header(name, value)
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
        except urllib.error.HTTPError as error:
            body = error.read()
            self.send_response(error.code)
            for name, value in error.headers.items():
                if name.lower() in FORWARD_HEADERS:
                    self.send_header(name, value)
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except (urllib.error.URLError, TimeoutError) as error:
            self._json_error(502, "OpenSky 연결 실패: %s" % getattr(error, "reason", error))

    def do_POST(self) -> None:  # noqa: N802
        path = urllib.parse.urlsplit(self.path).path
        if path != "/auth/token":
            self._json_error(404, "허용되지 않은 경로")
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._json_error(400, "잘못된 Content-Length")
            return
        if length <= 0 or length > 16_384:
            self._json_error(413, "인증 요청 크기 초과")
            return

        body = self.rfile.read(length)
        try:
            values = urllib.parse.parse_qs(body.decode("utf-8"), keep_blank_values=True)
        except UnicodeDecodeError:
            self._json_error(400, "인증 요청 인코딩 오류")
            return
        if (
            values.get("grant_type") != ["client_credentials"]
            or not values.get("client_id", [""])[0]
            or not values.get("client_secret", [""])[0]
        ):
            self._json_error(400, "clientId/clientSecret 형식 오류")
            return

        request = urllib.request.Request(
            AUTH_URL,
            data=body,
            method="POST",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
                "User-Agent": self.server_version,
            },
        )
        self._relay(request)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlsplit(self.path)
        if parsed.path != "/api/states/all":
            super().do_GET()
            return

        query = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
        if any(name not in STATE_PARAMS for name, _ in query):
            self._json_error(400, "허용되지 않은 항적 쿼리")
            return

        upstream = API_BASE + "/api/states/all"
        if query:
            upstream += "?" + urllib.parse.urlencode(query)
        headers = {"Accept": "application/json", "User-Agent": self.server_version}
        authorization = self.headers.get("Authorization", "")
        if authorization.startswith("Bearer ") and len(authorization) < 8192:
            headers["Authorization"] = authorization
        self._relay(urllib.request.Request(upstream, headers=headers))


def find_html() -> Path:
    for preferred in (
        ROOT / "RKSI_통합항로도_위성_v17.html",
        ROOT / "upload" / "RKSI_통합항로도_위성_v17.html",
    ):
        if preferred.is_file():
            return preferred
    matches = sorted(ROOT.glob("RKSI_*.html")) or sorted(ROOT.glob("*.html"))
    if not matches:
        raise FileNotFoundError("같은 폴더에서 RKSI HTML 파일을 찾지 못했습니다")
    return matches[0]


def main() -> int:
    parser = argparse.ArgumentParser(description="RKSI · RKSS OpenSky 로컬 프록시")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    html = find_html()
    handler = partial(OpenSkyHandler, directory=str(ROOT))

    try:
        server = ThreadingHTTPServer((HOST, args.port), handler)
    except OSError as error:
        print("서버 시작 실패:", error, file=sys.stderr)
        return 1

    relative_html = html.relative_to(ROOT).as_posix()
    url = "http://%s:%d/%s?proxy=1" % (HOST, args.port, urllib.parse.quote(relative_html, safe="/"))
    print("RKSI · RKSS OpenSky 로컬 서버 실행 중")
    print("브라우저 주소:", url)
    print("종료: 이 창에서 Ctrl+C")
    if not args.no_browser:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n서버를 종료합니다.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
