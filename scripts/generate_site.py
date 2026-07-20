#!/usr/bin/env python3
"""Generate the GitHub Pages site that lists the built Android APKs.

Scans every app under ``apps/<name>/``, locates its freshly built APK,
copies it into the output site directory and renders an ``index.html``
listing all of them for download.

Adding a new app is just a matter of dropping a new ``apps/<name>/`` Gradle
module with an ``app-info.json`` next to it; this script picks it up
automatically.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import shutil
from pathlib import Path


def human_size(num_bytes: int) -> str:
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} GB"


def read_app_info(app_dir: Path) -> dict:
    info_file = app_dir / "app-info.json"
    info: dict = {}
    if info_file.exists():
        info = json.loads(info_file.read_text(encoding="utf-8"))
    info.setdefault("name", app_dir.name.replace("-", " ").title())
    info.setdefault("description", "")
    info.setdefault("package", "")
    return info


def read_version(app_dir: Path) -> str:
    gradle = app_dir / "build.gradle.kts"
    if not gradle.exists():
        return ""
    text = gradle.read_text(encoding="utf-8")
    match = re.search(r'versionName\s*=\s*"([^"]+)"', text)
    return match.group(1) if match else ""


def find_apk(app_dir: Path) -> Path | None:
    """Return the best APK for an app, preferring release over debug."""
    apks = list((app_dir / "build" / "outputs" / "apk").rglob("*.apk"))
    if not apks:
        return None
    apks.sort(key=lambda p: (0 if "release" in p.parts else 1, p.name))
    return apks[0]


def render_html(apps: list[dict], generated_at: str) -> str:
    cards = []
    for app in apps:
        name = html.escape(app["name"])
        desc = html.escape(app["description"])
        pkg = html.escape(app["package"])
        version = html.escape(app["version"])
        meta_bits = []
        if version:
            meta_bits.append(f"v{version}")
        if pkg:
            meta_bits.append(pkg)
        meta_bits.append(app["size"])
        meta = " &middot; ".join(html.escape(b) if b != app["size"] else b for b in meta_bits)
        cards.append(
            f"""      <li class="card">
        <div class="card-body">
          <h2>{name}</h2>
          <p class="desc">{desc}</p>
          <p class="meta">{meta}</p>
        </div>
        <a class="download" href="{html.escape(app['apk_href'])}" download>Download APK</a>
      </li>"""
        )

    if cards:
        list_html = '<ul class="apps">\n' + "\n".join(cards) + "\n    </ul>"
    else:
        list_html = '<p class="empty">No apps have been built yet.</p>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>PxSandbox Android</title>
  <link rel="icon" type="image/svg+xml" href="icon.svg?v=2">
  <link rel="icon" type="image/png" sizes="512x512" href="icon-512.png?v=2">
  <link rel="apple-touch-icon" href="apple-touch-icon.png?v=2">
  <style>
    :root {{ color-scheme: light dark; }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #f6f7f9;
      color: #1b1b1f;
    }}
    @media (prefers-color-scheme: dark) {{
      body {{ background: #16181d; color: #e6e6e6; }}
      .card {{ background: #21242b !important; }}
    }}
    header {{
      background: linear-gradient(135deg, #6200ee, #9c47ff);
      color: #fff;
      padding: 48px 24px;
      text-align: center;
    }}
    header h1 {{ margin: 0 0 8px; font-size: 2rem; }}
    header p {{ margin: 0; opacity: 0.9; }}
    main {{ max-width: 760px; margin: 0 auto; padding: 24px; }}
    ul.apps {{ list-style: none; padding: 0; margin: 0; display: grid; gap: 16px; }}
    .card {{
      background: #fff;
      border-radius: 12px;
      padding: 20px;
      display: flex;
      align-items: center;
      gap: 16px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.12);
    }}
    .card-body {{ flex: 1; min-width: 0; }}
    .card h2 {{ margin: 0 0 4px; font-size: 1.25rem; }}
    .desc {{ margin: 0 0 8px; opacity: 0.85; }}
    .meta {{ margin: 0; font-size: 0.85rem; opacity: 0.6; word-break: break-word; }}
    a.download {{
      flex-shrink: 0;
      background: #6200ee;
      color: #fff;
      text-decoration: none;
      padding: 10px 18px;
      border-radius: 8px;
      font-weight: 600;
      white-space: nowrap;
    }}
    a.download:hover {{ background: #7722ff; }}
    .empty {{ text-align: center; opacity: 0.7; }}
    footer {{ text-align: center; padding: 24px; font-size: 0.8rem; opacity: 0.6; }}
  </style>
</head>
<body>
  <header>
    <h1>px-sandbox-android</h1>
    <p>Download the latest built APKs</p>
  </header>
  <main>
    {list_html}
  </main>
  <footer>
    Built automatically from the latest push &middot; {html.escape(generated_at)}
  </footer>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the APK download site.")
    parser.add_argument("--apps-dir", default="apps", type=Path)
    parser.add_argument("--output-dir", default="site", type=Path)
    args = parser.parse_args()

    apks_out = args.output_dir / "apks"
    apks_out.mkdir(parents=True, exist_ok=True)

    apps: list[dict] = []
    for app_dir in sorted(p for p in args.apps_dir.iterdir() if p.is_dir()):
        if not (app_dir / "build.gradle.kts").exists():
            continue
        apk = find_apk(app_dir)
        if apk is None:
            print(f"  ! no APK found for {app_dir.name}, skipping")
            continue
        dest_name = f"{app_dir.name}.apk"
        shutil.copy2(apk, apks_out / dest_name)
        info = read_app_info(app_dir)
        apps.append(
            {
                "name": info["name"],
                "description": info["description"],
                "package": info["package"],
                "version": read_version(app_dir),
                "size": human_size(apk.stat().st_size),
                "apk_href": f"apks/{dest_name}",
            }
        )
        print(f"  + {app_dir.name}: {apk} -> apks/{dest_name}")

    assets_dir = Path(__file__).resolve().parent.parent / "site-assets"
    if assets_dir.is_dir():
        for asset in assets_dir.iterdir():
            shutil.copy2(asset, args.output_dir / asset.name)

    generated_at = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    (args.output_dir / "index.html").write_text(
        render_html(apps, generated_at), encoding="utf-8"
    )
    print(f"Wrote {args.output_dir / 'index.html'} with {len(apps)} app(s).")


if __name__ == "__main__":
    main()
