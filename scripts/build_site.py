#!/usr/bin/env python3
"""Prepare the static GitHub Pages site and resolve its public asset URLs."""

import argparse
import shutil
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "site"
TARGET = ROOT / "_site"
PLACEHOLDER = "__PAGES_BASE_URL__"


def build_site(base_url: str, target: Path = TARGET, source: Path = SOURCE) -> Path:
    target = Path(target)
    base_url = base_url.strip().rstrip("/")
    parsed = urlsplit(base_url)
    if parsed.scheme != "https" or not parsed.netloc or parsed.query or parsed.fragment:
        raise ValueError("--base-url must be a public HTTPS URL without query or fragment")

    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(source, target)

    lua_path = target / "safetycar.lua"
    original = lua_path.read_text(encoding="utf-8")
    if original.count(PLACEHOLDER) != 1:
        raise ValueError("Expected exactly one base URL placeholder in safetycar.lua")
    lua_path.write_text(original.replace(PLACEHOLDER, base_url), encoding="utf-8")

    config = """; Race Control - Safety Car | CSP Online Script configuration
; Copy this section into your ACSM CSP Extra Options.
; For initial testing REQUIRED = 0; set REQUIRED = 1 only after verification.

[SCRIPT_RACE_CONTROL_SAFETY_CAR]
SCRIPT = {base_url}/safetycar.lua
REQUIRED = 0
REFRESH_PERIOD = 0
""".format(base_url=base_url)
    (target / "extra_options.ini").write_text(config, encoding="utf-8")

    for asset in ("safetycar.lua", "sc_on.wav", "sc_lights_off.wav", "index.html"):
        if not (target / asset).is_file():
            raise FileNotFoundError(f"Missing deploy asset: {asset}")

    return target


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", required=True, help="Base URL from actions/configure-pages")
    args = parser.parse_args()
    path = build_site(args.base_url)
    print(f"Prepared static site: {path}")
    print(f"Lua script: {args.base_url.rstrip('/')}/safetycar.lua")
    print(f"Configuration: {args.base_url.rstrip('/')}/extra_options.ini")


if __name__ == "__main__":
    main()
