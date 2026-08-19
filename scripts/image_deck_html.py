#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Create a browser-presentable fullscreen image slide deck."""

import argparse
import html
import os
from pathlib import Path


def rel_path(path: Path, output: Path) -> str:
    return Path(os.path.relpath(path.resolve(), output.parent.resolve())).as_posix()


def build_html(images: list[Path], output: Path, title: str) -> str:
    slides = []
    for index, image in enumerate(images, start=1):
        src = html.escape(rel_path(image, output))
        active = " active" if index == 1 else ""
        lazy = "" if index == 1 else ' loading="lazy"'
        slides.append(
            f'    <section class="slide{active}" aria-label="Slide {index}">'
            f'<img src="{src}" alt="Slide {index}"{lazy}></section>'
        )

    safe_title = html.escape(title)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{safe_title}</title>
  <style>
    * {{ box-sizing: border-box; }}
    html, body {{ margin: 0; width: 100%; height: 100%; overflow: hidden; background: #050505; color: #f5f5f5; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Helvetica Neue", Arial, sans-serif; }}
    main {{ position: fixed; inset: 0; display: grid; place-items: center; }}
    .slide {{
      position: absolute; inset: 0;
      display: none; place-items: center;
      background: #050505;
    }}
    .slide.active {{ display: grid; }}
    .slide img {{
      display: block;
      width: 100vw; height: 100vh;
      object-fit: contain;
      background: #050505;
    }}
    .hud {{
      position: fixed; left: 16px; right: 16px; bottom: 14px; z-index: 3;
      display: flex; justify-content: space-between; align-items: center;
      pointer-events: none;
      color: rgba(255,255,255,.82); font-size: 13px;
      text-shadow: 0 1px 8px rgba(0,0,0,.72);
    }}
    .title, .counter {{
      padding: 6px 9px; border-radius: 6px;
      background: rgba(0,0,0,.36); backdrop-filter: blur(10px);
    }}
    .nav {{
      position: fixed; top: 0; bottom: 0; z-index: 2;
      width: 28vw; border: 0; padding: 0; opacity: 0;
      cursor: pointer; background: transparent;
    }}
    .nav.prev {{ left: 0; }}
    .nav.next {{ right: 0; }}
    @media print {{
      html, body {{ overflow: visible; height: auto; background: #fff; }}
      main {{ position: static; display: block; }}
      .slide {{ position: static; display: block; break-after: page; background: #fff; }}
      .slide img {{ width: 100%; height: auto; object-fit: contain; }}
      .hud, .nav {{ display: none; }}
    }}
  </style>
</head>
<body>
  <main>
{chr(10).join(slides)}
  </main>
  <button class="nav prev" type="button" aria-label="上一页"></button>
  <button class="nav next" type="button" aria-label="下一页"></button>
  <div class="hud" aria-live="polite">
    <div class="title">{safe_title}</div>
    <div class="counter"><span id="current">1</span> / <span id="total">{len(images)}</span></div>
  </div>
  <script>
    const slides = Array.from(document.querySelectorAll('.slide'));
    const current = document.getElementById('current');
    const total = document.getElementById('total');
    let index = 0;

    total.textContent = String(slides.length);

    function show(nextIndex) {{
      index = Math.max(0, Math.min(slides.length - 1, nextIndex));
      slides.forEach((slide, i) => slide.classList.toggle('active', i === index));
      current.textContent = String(index + 1);
      const hash = `#${{index + 1}}`;
      if (location.hash !== hash) history.replaceState(null, '', hash);
    }}

    function step(delta) {{
      show(index + delta);
    }}

    document.querySelector('.nav.prev').addEventListener('click', () => step(-1));
    document.querySelector('.nav.next').addEventListener('click', () => step(1));
    document.addEventListener('keydown', (event) => {{
      if (['ArrowRight', 'ArrowDown', 'PageDown', ' '].includes(event.key)) {{
        event.preventDefault();
        step(1);
      }}
      if (['ArrowLeft', 'ArrowUp', 'PageUp', 'Backspace'].includes(event.key)) {{
        event.preventDefault();
        step(-1);
      }}
      if (event.key === 'Home') show(0);
      if (event.key === 'End') show(slides.length - 1);
    }});

    const initial = Number(location.hash.replace('#', ''));
    if (Number.isInteger(initial) && initial >= 1 && initial <= slides.length) {{
      show(initial - 1);
    }} else {{
      show(0);
    }}
  </script>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a fullscreen HTML image slide deck")
    parser.add_argument("images", nargs="+", help="Slide image paths")
    parser.add_argument("-o", "--output", required=True, help="Output HTML path")
    parser.add_argument("--title", default="Image Slide Deck", help="Document title")
    args = parser.parse_args()

    images = [Path(item) for item in args.images]
    missing = [str(path) for path in images if not path.exists()]
    if missing:
        raise SystemExit("Missing images:\n" + "\n".join(missing))

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(build_html(images, output, args.title), encoding="utf-8")
    print(f"HTML deck saved: {output.resolve()}")


if __name__ == "__main__":
    main()
