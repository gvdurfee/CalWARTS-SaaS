#!/usr/bin/env python3
"""Serve the demo. GET / returns index.html so Cursor can open the page."""

import os
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

def main() -> None:
    root = sys.argv[1]
    port = int(sys.argv[2])
    os.chdir(root)

    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self) -> None:
            path = self.path.split("?", 1)[0]
            if path in ("", "/"):
                self.path = "/index.html"
            super().do_GET()

        def log_message(self, fmt: str, *args) -> None:
            return

    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
