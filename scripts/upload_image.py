#!/usr/bin/env python3
"""Upload image (local path or URL) to ImgBB and print URL.

Usage:
  python3 [SKILL_DIR]/scripts/upload_image.py <image_path_or_url>

Auth:
  Requires IMGBB_API_KEY environment variable.

  The script auto-loads .env files (KEY=VALUE format) from these locations,
  in order. The first match wins, existing env vars are not overwritten:
    1. Current working directory: ./.env
    2. Skill root: [SKILL_DIR]/.env  (one level up from this script)
    3. User home: ~/.env

  Get a free key at https://api.imgbb.com (registration required).

Output:
  Final ImgBB image URL printed to stdout. Errors to stderr with exit code 1.
  No external Python dependencies—uses stdlib only.

Notes:
  - never prints the API key
  - accepts local file paths or remote http(s) URLs
  - works on Doubao / Codex / Claude Code / Cursor / any skills-compatible runtime
"""

from __future__ import annotations

import base64
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path


def _load_dotenv_if_present() -> None:
    """Minimal .env loader (KEY=VALUE). Tries CWD, skill root, ~/."""

    candidates = [
        Path.cwd() / ".env",
        Path(__file__).resolve().parents[1] / ".env",  # skill root
        Path.home() / ".env",
    ]

    for env_path in candidates:
        if not env_path.exists():
            continue
        try:
            for raw_line in env_path.read_text(encoding="utf-8").splitlines():
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = value
        except Exception:
            # best-effort; never block upload
            continue


def _is_url(s: str) -> bool:
    try:
        parsed = urllib.parse.urlparse(s)
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    except Exception:
        return False


def _read_bytes_from_url(url: str) -> bytes:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "huashu-slide-doubao/upload_image.py"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def _read_bytes_from_file(path: str) -> bytes:
    p = Path(path).expanduser().resolve()
    if not p.exists() or not p.is_file():
        raise FileNotFoundError(f"File not found: {p}")
    return p.read_bytes()


def upload_to_imgbb(image_bytes: bytes, api_key: str) -> str:
    encoded = base64.b64encode(image_bytes).decode("ascii")

    form_data = urllib.parse.urlencode(
        {"key": api_key, "image": encoded}
    ).encode("ascii")

    req = urllib.request.Request(
        "https://api.imgbb.com/1/upload",
        data=form_data,
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read().decode("utf-8")
            status = resp.status
    except urllib.error.HTTPError as e:
        # try to surface ImgBB's error message
        try:
            body = e.read().decode("utf-8")
            payload = json.loads(body)
            msg = (payload.get("error") or {}).get("message") or f"HTTP {e.code}"
        except Exception:
            msg = f"HTTP {e.code}"
        raise RuntimeError(f"ImgBB upload failed: {msg}")

    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        raise RuntimeError(f"ImgBB response not JSON (status {status})")

    if not payload.get("success"):
        msg = (payload.get("error") or {}).get("message") or f"HTTP {status}"
        raise RuntimeError(f"ImgBB upload failed: {msg}")

    data = payload.get("data") or {}
    url = data.get("url") or data.get("display_url")
    if not url:
        raise RuntimeError("ImgBB upload failed: missing url in response")
    return url


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] in {"-h", "--help"}:
        print(__doc__.strip())
        return 0

    _load_dotenv_if_present()

    api_key = os.getenv("IMGBB_API_KEY")
    if not api_key:
        print(
            "Error: IMGBB_API_KEY is not set. "
            "Set it as env var or in .env (cwd / skill root / ~/.env). "
            "Get a free key at https://api.imgbb.com",
            file=sys.stderr,
        )
        return 2

    source = sys.argv[1]
    try:
        image_bytes = _read_bytes_from_url(source) if _is_url(source) else _read_bytes_from_file(source)
        url = upload_to_imgbb(image_bytes, api_key)
        print(url)
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
