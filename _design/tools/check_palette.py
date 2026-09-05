#!/usr/bin/env python3
"""Assert the Bone & Navy palette meets WCAG AA against the page ground.

Parses the real `$name: #hex;` declarations out of assets/theme.scss so the
test fails if someone edits a colour without rechecking contrast.
"""
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
THEME = REPO / "assets" / "theme.scss"

GROUND = "paper"
# variable name -> minimum contrast ratio against the ground
REQUIRED = {
    "ink": 4.5,
    "body-ink": 4.5,
    "muted": 4.5,
    "navy": 4.5,
}
# these are non-text and only need to be present, not contrasty
PRESENT_ONLY = ["rule", "navy-line"]


def parse_colours(text):
    out = {}
    for name, hexval in re.findall(r"^\$([a-z0-9-]+):\s*(#[0-9A-Fa-f]{6})\s*;", text, re.M):
        out[name] = hexval
    return out


def luminance(hexval):
    r, g, b = (int(hexval[i:i + 2], 16) / 255 for i in (1, 3, 5))
    def lin(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = lin(r), lin(g), lin(b)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def main():
    if not THEME.exists():
        print(f"FAIL: {THEME} does not exist")
        return 1

    colours = parse_colours(THEME.read_text(encoding="utf-8"))
    failures = []

    if GROUND not in colours:
        print(f"FAIL: ${GROUND} not declared in theme.scss")
        return 1
    ground = colours[GROUND]

    for name in PRESENT_ONLY:
        if name not in colours:
            failures.append(f"${name} not declared")

    for name, minimum in REQUIRED.items():
        if name not in colours:
            failures.append(f"${name} not declared")
            continue
        ratio = contrast(colours[name], ground)
        status = "ok " if ratio >= minimum else "FAIL"
        print(f"  {status} ${name:<10} {colours[name]}  {ratio:5.2f} : 1  (min {minimum})")
        if ratio < minimum:
            failures.append(f"${name} is {ratio:.2f}:1, needs {minimum}:1")

    if failures:
        print("\nFAIL:")
        for f in failures:
            print(f"  - {f}")
        return 1

    print(f"\nPASS: all text colours meet WCAG AA on ${GROUND} {ground}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
