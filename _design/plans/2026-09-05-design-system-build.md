# Design System Build Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild andresjuve.com on the Bone & Navy token system — Spectral + Archivo, a fixed metadata grid, no cards — and add Teaching and Practice pages.

**Architecture:** One SCSS file (`assets/theme.scss`) is the only stylesheet. Its `scss:defaults` block holds the palette and font stacks as SCSS variables (so Bootstrap can be remapped) and its `scss:rules` block re-exposes those same literals as CSS custom properties in `:root`, then styles six components against them. Pages are `.qmd` files built from Quarto fenced divs — adding a paper means copying one block. No JavaScript, no partials, no Lua filters.

**Tech Stack:** Quarto 1.10.18 (website project), Bootstrap via the `cosmo` theme, SCSS, Google Fonts (Spectral, Archivo), Python 3 for the palette test, Playwright MCP for screenshots.

**Spec:** `_design/2026-09-05-design-system.md` — read it before starting. Every token value in this plan is copied from it.

## Global Constraints

- **Quarto is not on PATH.** Every render uses the Positron bundle. Define once per shell:
  `QUARTO="/c/Users/s12600/AppData/Local/Programs/Positron/resources/app/quarto/bin/quarto.exe"`
- **Kill any static server serving `docs/` before rendering.** Quarto deletes and recreates `docs/`; an open server causes `os error 32`. Check with
  `powershell -c "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Where-Object { \$_.CommandLine -like '*http.server*' }"`
- **Light theme only.** No dark palette, no `prefers-color-scheme` block, no theme-toggle JS.
- **No cards.** No `background` fills on content blocks, no `box-shadow`, no `border-radius` anywhere. `$border-radius: 0` globally.
- **Two rules only.** `1px solid var(--ink)` means "new section". `1px solid var(--rule)` means "next item". No other border is permitted on a content element.
- **Exact palette** (do not round or re-pick): `--paper #FAF9F6`, `--ink #14161A`, `--body #4A4F57`, `--muted #676D76`, `--rule #DDDAD1`, `--navy #14346B`, `--navy-line #B9C4DA`.
- **Exact type:** `"Spectral", Georgia, "Times New Roman", serif` and `"Archivo", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif`. Weights loaded: Spectral 400, 400i, 500; Archivo 500, 600. Load no other weights.
- **One breakpoint:** `720px`. If a second seems necessary, stop and report — the grid is wrong.
- **No commits are pushed.** Commit locally per task; the owner reviews before any push.
- **Screenshots** go to `.playwright-mcp/` (gitignored). Serve the built site with
  `cd docs && python -m http.server 8899 --bind 127.0.0.1` and always kill it before the next render.

---

### Task 1: Palette test and the token layer

Establishes the single source of truth. The test is genuine: it parses the real hex values out of the stylesheet and fails the build if any text colour drops below WCAG AA on the page ground.

**Files:**
- Create: `_design/tools/check_palette.py`
- Create: `assets/theme.scss`
- Modify: `_quarto.yml`

**Interfaces:**
- Consumes: nothing.
- Produces: SCSS variables `$paper $ink $body-ink $muted $rule $navy $navy-line $serif $sans`, and CSS custom properties `--paper --ink --body --muted --rule --navy --navy-line --fs-display --fs-page-title --fs-lead --fs-section --fs-title --fs-body --fs-sub --fs-label --fs-meta --sp-1..--sp-6 --measure --col-meta --gutter --page-max`. Every later task styles against these names and no literals.

- [ ] **Step 1: Write the failing test**

Create `_design/tools/check_palette.py`:

```python
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
```

- [ ] **Step 2: Run it to make sure it fails**

```bash
python _design/tools/check_palette.py
```

Expected: `FAIL: .../assets/theme.scss does not exist` and exit code 1. (`assets/theme.scss` currently holds the old Linen Fjord theme, so if it exists the test will instead fail on `$paper not declared` — either failure is the correct starting state.)

- [ ] **Step 3: Write the token layer**

Replace the whole of `assets/theme.scss` with:

```scss
/*-- scss:defaults --*/

// ===========================================================================
//  Bone & Navy — see _design/2026-09-05-design-system.md
//  These seven hexes are the only colours in the system. Change one here and
//  the whole site follows. Re-run _design/tools/check_palette.py afterwards.
// ===========================================================================
$paper:      #FAF9F6;   // page ground, barely-warm white
$ink:        #14161A;   // name, titles, section heads, strong rules
$body-ink:   #4A4F57;   // running text, coauthor lines
$muted:      #676D76;   // metadata column, nav, labels
$rule:       #DDDAD1;   // hairline between entries
$navy:       #14346B;   // links, metadata identifying line, focus ring
$navy-line:  #B9C4DA;   // link underlines only

// Type ----------------------------------------------------------------------
@import url('https://fonts.googleapis.com/css2?family=Archivo:wght@500;600&family=Spectral:ital,wght@0,400;0,500;1,400&display=swap');

$serif: "Spectral", Georgia, "Times New Roman", serif;
$sans:  "Archivo", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;

// Bootstrap / Quarto remapping ----------------------------------------------
// Body text is the serif; the sans is reserved for labels only.
$font-family-sans-serif: $serif;
$headings-font-family:   $serif;
$headings-font-weight:   500;

$body-bg:        $paper;
$body-color:     $body-ink;
$headings-color: $ink;

$primary:   $navy;
$secondary: $muted;

$link-color:            $navy;
$link-decoration:       none;
$link-hover-color:      $navy;
$link-hover-decoration: none;

$border-color: $rule;
$navbar-fg:    $muted;

// No cards means no radius, anywhere.
$border-radius:    0;
$border-radius-sm: 0;
$border-radius-lg: 0;
$border-radius-xl: 0;

/*-- scss:rules --*/

// ===========================================================================
//  Tokens. Components below reference only these — never a literal.
// ===========================================================================
:root {
  --paper:      #{$paper};
  --ink:        #{$ink};
  --body:       #{$body-ink};
  --muted:      #{$muted};
  --rule:       #{$rule};
  --navy:       #{$navy};
  --navy-line:  #{$navy-line};

  --serif: #{$serif};
  --sans:  #{$sans};

  --fs-display:    clamp(2.2rem, 5.2vw, 3.25rem);
  --fs-page-title: clamp(1.9rem, 4vw, 2.5rem);
  --fs-lead:       1.05rem;
  --fs-section:    1.12rem;
  --fs-title:      1.16rem;
  --fs-body:       1rem;
  --fs-sub:        0.95rem;
  --fs-label:      0.68rem;
  --fs-meta:       0.68rem;

  --sp-1: 0.25rem;
  --sp-2: 0.5rem;
  --sp-3: 1rem;
  --sp-4: 1.5rem;
  --sp-5: 2.25rem;
  --sp-6: 3.5rem;

  --measure:  54ch;
  --col-meta: 9rem;
  --gutter:   2.75rem;
  --page-max: 46rem;
}

body {
  font-family: var(--serif);
  font-size: var(--fs-body);
  line-height: 1.62;
  background: var(--paper);
  color: var(--body);
  -webkit-font-smoothing: antialiased;
}

// Focus is never removed.
:focus-visible {
  outline: 2px solid var(--navy);
  outline-offset: 3px;
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

- [ ] **Step 4: Run the test to verify it passes**

```bash
python _design/tools/check_palette.py
```

Expected output, exit code 0:

```
  ok  $ink        #14161A  17.20 : 1  (min 4.5)
  ok  $body-ink   #4A4F57   7.83 : 1  (min 4.5)
  ok  $muted      #676D76   4.95 : 1  (min 4.5)
  ok  $navy       #14346B  11.51 : 1  (min 4.5)

PASS: all text colours meet WCAG AA on $paper #FAF9F6
```

If any ratio differs by more than 0.02 from these numbers, a hex was mistyped — fix the hex, do not adjust the test.

- [ ] **Step 5: Point Quarto at the theme and drop the stale title**

In `_quarto.yml`, change the site title from the abbreviation to the full name (the spec's navbar component specifies the full name), and confirm the theme list. Replace the `website:` title line and the `format:` block so they read:

```yaml
website:
  title: "André Wattø Sjuve"
```

```yaml
format:
  html:
    theme:
      - cosmo
      - assets/theme.scss
    highlight-style: github
    pagetitle: "{{< meta title >}}"
    lightbox: true
```

Leave `project:`, `navbar:`, `page-footer:` and `execute:` untouched in this task.

- [ ] **Step 6: Render to confirm the SCSS compiles**

```bash
QUARTO="/c/Users/s12600/AppData/Local/Programs/Positron/resources/app/quarto/bin/quarto.exe"
"$QUARTO" render
```

Expected: `Output created: docs\index.html`, exit code 0. A SCSS syntax error surfaces here as a `sass` error naming the line.

- [ ] **Step 7: Confirm the tokens reached the compiled CSS**

```bash
grep -c -- '--fs-display' docs/site_libs/bootstrap/bootstrap-*.min.css
grep -o -- '--paper:[^;]*' docs/site_libs/bootstrap/bootstrap-*.min.css | head -1
```

Expected: count `1` or more, and `--paper:#faf9f6` (case may vary).

- [ ] **Step 8: Commit**

```bash
git add _design/tools/check_palette.py assets/theme.scss _quarto.yml
git commit -m "Add Bone & Navy token layer and palette contrast test"
```

---

### Task 2: Chrome — navbar, page container, footer, page title

Everything that frames content. Gets the measure and the two rules established before any component is built on top.

**Files:**
- Modify: `assets/theme.scss` (append to `scss:rules`)

**Interfaces:**
- Consumes: all tokens from Task 1.
- Produces: `main.content` constrained to `--page-max`; `.navbar` and `.nav-footer` styled; `main.content > h1` styled as the page-title variant of the hero component. Tasks 4–7 assume page `h1` needs no further styling.

- [ ] **Step 1: Append the chrome rules**

Add to the end of `assets/theme.scss`:

```scss
// ===========================================================================
//  6.1 Navbar
// ===========================================================================
.navbar {
  background: var(--paper);
  border-bottom: 1px solid var(--ink);
  padding-top: var(--sp-3);
  padding-bottom: var(--sp-2);
}

.navbar > .container-fluid,
.navbar > .container {
  max-width: var(--page-max);
  padding-left: 0;
  padding-right: 0;
}

.navbar-title {
  font-family: var(--serif);
  font-style: italic;
  font-weight: 500;
  font-size: 1.02rem;
  letter-spacing: 0;
  color: var(--ink);
}

.navbar-nav .nav-link {
  font-family: var(--sans);
  font-size: var(--fs-label);
  font-weight: 500;
  letter-spacing: 0.13em;
  text-transform: uppercase;
  color: var(--muted) !important;
  padding-bottom: 2px !important;
  margin: 0 0 0 var(--sp-3);
  border-bottom: 1px solid transparent;
}

.navbar-nav .nav-link:hover,
.navbar-nav .nav-link[aria-current="page"],
.navbar-nav .nav-link.active {
  color: var(--navy) !important;
  border-bottom-color: var(--navy);
}

.navbar .quarto-navbar-tools .nav-link { color: var(--muted) !important; }

// ===========================================================================
//  Page container — one measure for the whole site
// ===========================================================================
main.content {
  max-width: var(--page-max);
  margin-inline: auto;
  padding-top: var(--sp-6);
  padding-bottom: var(--sp-6);
}

// ===========================================================================
//  6.2 Page title (the hero's second variant; hero itself is Task 3)
// ===========================================================================
main.content > h1 {
  font-family: var(--serif);
  font-weight: 400;
  font-size: var(--fs-page-title);
  line-height: 1.06;
  letter-spacing: -0.018em;
  color: var(--ink);
  margin: 0 0 var(--sp-4);
  padding-bottom: var(--sp-4);
  border-bottom: 1px solid var(--rule);
}

// An orienting sentence directly under a page title.
.page-lead {
  font-size: var(--fs-lead);
  max-width: var(--measure);
  color: var(--body);
  margin: calc(var(--sp-4) * -1 + var(--sp-2)) 0 var(--sp-4);
}

// ===========================================================================
//  Footer
// ===========================================================================
.nav-footer {
  border-top: 1px solid var(--rule);
  background: var(--paper);
  color: var(--muted);
  font-size: var(--fs-sub);
}
.nav-footer a { color: var(--muted); }
```

- [ ] **Step 2: Render**

```bash
QUARTO="/c/Users/s12600/AppData/Local/Programs/Positron/resources/app/quarto/bin/quarto.exe"
"$QUARTO" render
```

Expected: exit code 0.

- [ ] **Step 3: Verify the container width actually applied**

Quarto's page scaffolding varies by `page-layout`; this step catches a selector that silently missed.

```bash
cd docs && python -m http.server 8899 --bind 127.0.0.1 &
sleep 2
```

Then via Playwright MCP, in one `browser_run_code_unsafe` call:

```js
async (page) => {
  await page.setViewportSize({ width: 1280, height: 900 });
  await page.goto('http://127.0.0.1:8899/research/', { waitUntil: 'networkidle' });
  const main = await page.$('main.content');
  const box = await main.boundingBox();
  await page.screenshot({ path: '.playwright-mcp/t2-research.png', fullPage: true, scale: 'css' });
  return JSON.stringify(box);
}
```

Expected: width between `700` and `760` (46rem ≈ 736px). If it is ~1100 or the full viewport, the `main.content` selector missed — inspect the rendered HTML with `grep -o '<main[^>]*>' docs/research/index.html` and adjust the selector to match the real class, then re-render and re-check.

Kill the server before continuing:

```bash
powershell -c "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Where-Object { \$_.CommandLine -like '*http.server*' } | ForEach-Object { Stop-Process -Id \$_.ProcessId -Force }"
```

- [ ] **Step 4: Commit**

```bash
git add assets/theme.scss
git commit -m "Style navbar, page container, page title and footer"
```

---

### Task 3: Hero — and the Spectral-on-bone verification gate

The spec's §11 makes this a verification before it is a build: Spectral has never been rendered on `#FAF9F6`. If the texture is wrong, everything downstream is wrong, so it is checked here and nowhere later.

**Files:**
- Modify: `assets/theme.scss` (append)
- Modify: `index.qmd` (full rewrite)

**Interfaces:**
- Consumes: tokens from Task 1, container from Task 2.
- Produces: CSS classes `.hero`, `.hero-meta`, `.hero-name`, `.hero-lead`. The `--col-meta` + `--gutter` grid established here is reused verbatim by the entry component in Task 4.

- [ ] **Step 1: Append the hero rules**

Add to the end of `assets/theme.scss`:

```scss
// ===========================================================================
//  6.2 Hero (home only)
// ===========================================================================
.hero {
  display: grid;
  gap: var(--sp-3);
  padding-bottom: var(--sp-5);
  border-bottom: 1px solid var(--rule);
}

@media (min-width: 720px) {
  .hero {
    grid-template-columns: var(--col-meta) minmax(0, 1fr);
    gap: 0 var(--gutter);
  }
}

.hero-meta {
  font-family: var(--sans);
  font-size: var(--fs-meta);
  font-weight: 500;
  letter-spacing: 0.09em;
  text-transform: uppercase;
  color: var(--muted);
  line-height: 1.85;
  padding-top: 0.5rem;
  margin: 0;
}

.hero-name {
  font-family: var(--serif);
  font-weight: 400;
  font-size: var(--fs-display);
  line-height: 1.02;
  letter-spacing: -0.018em;
  color: var(--ink);
  margin: 0 0 var(--sp-3);
}

.hero-lead {
  font-size: var(--fs-lead);
  max-width: var(--measure);
  color: var(--body);
  margin: 0;
}
```

- [ ] **Step 2: Rewrite `index.qmd`**

Replace the whole file with:

```markdown
---
pagetitle: "André Wattø Sjuve"
toc: false
---

::: {.hero}
::: {.hero-meta}
Associate\
Professor\
NHH · Bergen
:::

::: {}
[André Wattø Sjuve]{.hero-name}

[I study asset management — what active managers actually deliver, what investors pay for it, and how regulation changes both. I am at the [Department of Business and Management Science](https://www.nhh.no/en/employees/faculty/andre-watto-sjuve/) at NHH Norwegian School of Economics.]{.hero-lead}
:::
:::
```

Note: `.hero-name` and `.hero-lead` are applied to spans via bracketed spans, so they need `display: block` to lay out. Add to `assets/theme.scss` immediately after the `.hero-lead` rule:

```scss
.hero-name,
.hero-lead,
.page-lead { display: block; }
```

- [ ] **Step 3: Render**

```bash
QUARTO="/c/Users/s12600/AppData/Local/Programs/Positron/resources/app/quarto/bin/quarto.exe"
"$QUARTO" render
```

Expected: exit code 0.

- [ ] **Step 4: THE GATE — look at Spectral on bone at both widths**

```bash
cd docs && python -m http.server 8899 --bind 127.0.0.1 &
sleep 2
```

Playwright, one call:

```js
async (page) => {
  await page.setViewportSize({ width: 1280, height: 900 });
  await page.goto('http://127.0.0.1:8899/', { waitUntil: 'networkidle' });
  await page.screenshot({ path: '.playwright-mcp/t3-home-1280.png', fullPage: true, scale: 'css' });
  await page.setViewportSize({ width: 480, height: 900 });
  await page.reload({ waitUntil: 'networkidle' });
  await page.screenshot({ path: '.playwright-mcp/t3-home-480.png', fullPage: true, scale: 'css' });
  const f = await page.evaluate(() => getComputedStyle(document.querySelector('.hero-name')).fontFamily);
  return f;
}
```

Two checks, both must pass:

1. The returned font family must begin with `Spectral`. If it says `Georgia` or `Times`, the Google Fonts `@import` did not load — confirm the `@import` is the first statement in `scss:defaults` and that the weights `0,400;0,500;1,400` are present in the URL.
2. Read both screenshots. Confirm: the name is not too light against `#FAF9F6`; the metadata column and the name sit on the same left edge at 1280px; the grid has collapsed to one column at 480px with metadata above the name; no horizontal scrollbar at 480px.

**If the texture is wrong, stop and report to the owner before continuing.** The fallback agreed in the type study is candidate 01, Source Serif 4 — swapping it is a two-line change in `scss:defaults` (`$serif` and the `@import`), but it is the owner's call, not the implementer's.

Kill the server.

- [ ] **Step 5: Commit**

```bash
git add assets/theme.scss index.qmd
git commit -m "Add hero component and rebuild the home page on it"
```

---

### Task 4: The entry component, and Research rebuilt on it

The core of the system. One component, three uses; this task builds it and proves it with the publication use.

**Files:**
- Modify: `assets/theme.scss` (append)
- Modify: `research/index.qmd` (full rewrite)

**Interfaces:**
- Consumes: tokens from Task 1, the grid from Task 3.
- Produces: CSS classes `.sect`, `.sect-tag`, `.entry`, `.entry-meta`, `.entry-org`, `.entry-title`, `.entry-sub`, `.entry-links`, `.paper-link`, and styling for `details.abstract`. Tasks 5, 6 and 7 reuse all of these unchanged and add no new classes.

- [ ] **Step 1: Append the section head, entry, link and disclosure rules**

Add to the end of `assets/theme.scss`:

```scss
// ===========================================================================
//  6.3 Section head
// ===========================================================================
.sect {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: var(--sp-3);
  border-bottom: 1px solid var(--ink);
  padding-bottom: var(--sp-1);
  margin: var(--sp-5) 0 0;
}

main.content h2 {
  font-family: var(--serif);
  font-style: italic;
  font-weight: 500;
  font-size: var(--fs-section);
  line-height: 1.3;
  color: var(--ink);
  margin: 0;
  border: 0;
  padding: 0;
}

.sect-tag {
  font-family: var(--sans);
  font-size: var(--fs-label);
  font-weight: 500;
  letter-spacing: 0.13em;
  text-transform: uppercase;
  color: var(--muted);
  white-space: nowrap;
}

// ===========================================================================
//  6.4 Entry — publications, courses and engagements are all this
// ===========================================================================
.entry {
  display: grid;
  gap: var(--sp-1);
  padding: var(--sp-3) 0;
  border-bottom: 1px solid var(--rule);
}

@media (min-width: 720px) {
  .entry {
    grid-template-columns: var(--col-meta) minmax(0, 1fr);
    gap: var(--sp-1) var(--gutter);
  }
  .entry-meta { grid-row: span 4; }
}

.entry:last-of-type { border-bottom: 0; }

.entry-meta {
  font-family: var(--sans);
  font-size: var(--fs-meta);
  font-weight: 500;
  letter-spacing: 0.09em;
  text-transform: uppercase;
  color: var(--muted);
  font-variant-numeric: tabular-nums;
  line-height: 1.6;
  padding-top: 0.4rem;
  margin: 0;
}

// The identifying line: journal, course code, or institution.
.entry-org {
  display: block;
  font-weight: 600;
  letter-spacing: 0.07em;
  color: var(--navy);
}

.entry-title {
  display: block;
  font-family: var(--serif);
  font-weight: 500;
  font-size: var(--fs-title);
  line-height: 1.32;
  letter-spacing: -0.005em;
  color: var(--ink);
  text-wrap: balance;
  margin: 0;
}

.entry-sub {
  display: block;
  font-size: var(--fs-sub);
  line-height: 1.55;
  color: var(--body);
  margin: 0;
}

// Quarto wraps loose text in <p>; keep those from adding their own space.
.entry p { margin: 0; }

// ===========================================================================
//  6.5 Link — not a button
// ===========================================================================
.entry-links {
  display: flex;
  flex-wrap: wrap;
  gap: var(--sp-3);
  margin-top: var(--sp-2);
}

.paper-link {
  font-family: var(--sans);
  font-size: var(--fs-label);
  font-weight: 500;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--navy);
  text-decoration: none !important;
  border-bottom: 1px solid var(--navy-line);
  padding-bottom: 1px;
}

.paper-link:hover { border-bottom-color: var(--navy); }

// ===========================================================================
//  6.6 Abstract disclosure — native <details>
// ===========================================================================
details.abstract { margin-top: var(--sp-2); }

details.abstract > summary {
  cursor: pointer;
  font-family: var(--sans);
  font-size: var(--fs-label);
  font-weight: 500;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--muted);
  list-style: none;
}

details.abstract > summary::-webkit-details-marker { display: none; }
details.abstract > summary::before { content: "+ "; }
details.abstract[open] > summary::before { content: "– "; }
details.abstract > summary:hover { color: var(--navy); }

details.abstract p {
  font-size: var(--fs-body);
  max-width: var(--measure);
  color: var(--body);
  margin: var(--sp-2) 0 0;
}

// Body links inside prose, distinct from .paper-link
main.content p a:not(.paper-link) {
  color: var(--navy);
  border-bottom: 1px solid var(--navy-line);
}
main.content p a:not(.paper-link):hover { border-bottom-color: var(--navy); }
```

- [ ] **Step 2: Rewrite `research/index.qmd`**

The two government/industry reports move to Practice in Task 5, so they are absent here. Replace the whole file with:

```markdown
---
title: "Research"
toc: false
---

::: {.sect}
## Published & forthcoming

[Peer reviewed]{.sect-tag}
:::

::: {.entry}
[[Journal of Portfolio Management]{.entry-org}Forthcoming]{.entry-meta}

[Where Active Management Adds Value for a Large Asset Owner]{.entry-title}

[with Trond Døskeland]{.entry-sub}

<details class="abstract"><summary>Abstract</summary>
<p>We study how one large benchmarked asset owner allocated scarce active-risk budget across active functions, using evidence from Norway's sovereign wealth fund. Using fund-level data from 1998 through 2025 and strategy-level evidence from 2013 through 2025, we find that the most consistent gains came from implementation-oriented activities that scaled well across a very large portfolio. Equity security selection also added value, though less uniformly. Discretionary allocation, by contrast, reduced benchmark-relative returns on average. Although Norway's fund is institutionally distinctive, the evidence suggests that where investors share similar benchmark governance, scale, and implementation capacity, the strongest case for active management may lie in repeatable implementation advantages and selected forms of specialized security selection.</p>
</details>
:::

::: {.entry}
[[Management Science]{.entry-org}September 2025]{.entry-meta}

[Forced to Be Active: Evidence From a Regulation Intervention]{.entry-title}

[with Petter Bjerksund, Trond Døskeland and Andreas Ørpetveit]{.entry-sub}

::: {.entry-links}
[Publisher](https://doi.org/10.1287/mnsc.2023.03124){.paper-link}
[SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3635718){.paper-link}
:::

<details class="abstract"><summary>Abstract</summary>
<p>Mutual funds known as closet indexers are marketed as active, but actually operate as low-activity funds. Investors end up paying for full service, but only receiving a part of it. Supervisory authorities around the world are considering ways to regulate these funds. In this context, we examine the impact of regulatory interventions by Scandinavian regulators. We compare the scrutinized Scandinavian funds with similar unaffected European funds. The findings suggest that the regulated Scandinavian funds preferred increased activity over fee reduction. Consequently, fund managers adopted more active management strategies, resulting in a significant 2% decrease in annual alpha. Therefore, the regulatory interventions resulted in unfavorable outcomes for investors.</p>
</details>
:::

::: {.entry}
[[Journal of Empirical Finance]{.entry-org}March 2025]{.entry-meta}

[Do Fees Matter? Investor's Sensitivity to Active Management Fees]{.entry-title}

[with Trond Døskeland and Andreas Ørpetveit]{.entry-sub}

::: {.entry-links}
[Publisher](https://doi.org/10.1016/j.jempfin.2025.101596){.paper-link}
[SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3857628){.paper-link}
:::

<details class="abstract"><summary>Abstract</summary>
<p>Following the framework established by Berk and Green (2004), mutual fund inflows and fees should be uncorrelated at equilibrium. We empirically explore this relationship by investigating the temporal changes in fund fees and flows. Our fee metrics focus on active management services rather than diversification. We analyze the additional fee compared to passive alternatives and additional fee per unit of active management, along with the traditionally used total fee. Our analysis of global data reveals a negative time series correlation between both measures of active management fee and fund flows.</p>
</details>
:::

::: {.sect}
## Manuscripts being prepared

[Working papers]{.sect-tag}
:::

::: {.entry}
[[Under review]{.entry-org}Single authored]{.entry-meta}

[Sustainable, But Not Price-Blind: Fee Sensitivity in ESG Mutual Fund Flows]{.entry-title}

::: {.entry-links}
[SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4187059){.paper-link}
:::
:::

::: {.entry}
[[In progress]{.entry-org}]{.entry-meta}

[Two-Dimensional Activeness: Exploring the Interplay Between Active Ownership and Active Portfolio Management]{.entry-title}

[with Trond Døskeland, Xuan Li and Andreas Ørpetveit]{.entry-sub}
:::
```

- [ ] **Step 3: Render**

```bash
QUARTO="/c/Users/s12600/AppData/Local/Programs/Positron/resources/app/quarto/bin/quarto.exe"
"$QUARTO" render
```

Expected: exit code 0.

- [ ] **Step 4: Verify the entry grid and that nothing became a card**

```bash
cd docs && python -m http.server 8899 --bind 127.0.0.1 &
sleep 2
```

Playwright, one call:

```js
async (page) => {
  await page.setViewportSize({ width: 1280, height: 900 });
  await page.goto('http://127.0.0.1:8899/research/', { waitUntil: 'networkidle' });
  await page.screenshot({ path: '.playwright-mcp/t4-research-1280.png', fullPage: true, scale: 'css' });
  await page.setViewportSize({ width: 480, height: 900 });
  await page.reload({ waitUntil: 'networkidle' });
  await page.screenshot({ path: '.playwright-mcp/t4-research-480.png', fullPage: true, scale: 'css' });
  return await page.evaluate(() => {
    const e = document.querySelector('.entry');
    const cs = getComputedStyle(e);
    const org = document.querySelector('.entry-org');
    return JSON.stringify({
      radius: cs.borderRadius,
      shadow: cs.boxShadow,
      bg: cs.backgroundColor,
      orgColour: getComputedStyle(org).color,
      entries: document.querySelectorAll('.entry').length
    });
  });
}
```

Expected: `radius` `0px`, `shadow` `none`, `bg` `rgba(0, 0, 0, 0)`, `orgColour` `rgb(20, 52, 107)`, `entries` `5`. Any non-zero radius or a solid background means a card crept in — find and remove it.

Then read both screenshots and confirm: journal names read as a scannable column down the left; section heads are visibly stronger than the metadata inside entries; abstracts are collapsed by default.

Kill the server.

- [ ] **Step 5: Commit**

```bash
git add assets/theme.scss research/index.qmd
git commit -m "Add entry component and rebuild Research on it"
```

---

### Task 5: Practice page

Receives the two reports moved out of Research, plus the policy and consulting work that has until now existed only inside the CV PDF.

**Files:**
- Create: `practice/index.qmd`
- Modify: `_quarto.yml` (navbar)

**Interfaces:**
- Consumes: every class from Task 4 unchanged. Adds no new CSS.
- Produces: `/practice/` in the site; the navbar order Home · Research · Teaching · Practice · CV is finalised in Task 6.

- [ ] **Step 1: Create `practice/index.qmd`**

```markdown
---
title: "Practice"
toc: false
---

[Work for public bodies, asset owners and the profession, alongside the academic research.]{.page-lead}

::: {.sect}
## Appointments & advisory

[Selected]{.sect-tag}
:::

::: {.entry}
[[Ministry of Finance]{.entry-org}2025]{.entry-meta}

[Committee member, evaluation of the Government Pension Fund Global]{.entry-title}

[Appointed to the committee assessing active management in Norway's sovereign wealth fund.]{.entry-sub}
:::

::: {.entry}
[[Magma]{.entry-org}2026]{.entry-meta}

[Subject editor — investments outside the stock exchange]{.entry-title}

[Magma forskning og viten, volume 29, issue 2.]{.entry-sub}
:::

::: {.entry}
[[KLP]{.entry-org}2024]{.entry-meta}

[Consultant, report on the economic role of KLP]{.entry-title}
:::

::: {.entry}
[[Norsk legemiddelforsikring]{.entry-org}2024]{.entry-meta}

[Consultant, review of investment strategy]{.entry-title}
:::

::: {.entry}
[[Pensjonskontoret]{.entry-org}2023]{.entry-meta}

[Consultant, returns from asset management of public pensions]{.entry-title}
:::

::: {.entry}
[[Ministry of Finance]{.entry-org}2022]{.entry-meta}

[Code reviewer, evaluation of the Government Pension Fund Global]{.entry-title}
:::

::: {.sect}
## Reports

[Public &amp; industry]{.sect-tag}
:::

::: {.entry}
[[Government report]{.entry-org}December 2025]{.entry-meta}

[Evaluating the Performance of Active Management in Norway's Sovereign Wealth Fund (GPFG)]{.entry-title}

[with Trond Døskeland]{.entry-sub}

::: {.entry-links}
[SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5887182){.paper-link}
:::

<details class="abstract"><summary>Abstract</summary>
<p>This report concludes that Norges Bank's active management of the Fund has created substantial value for the Norwegian people. Since 1998, active decisions have contributed about 611 billion NOK before costs, and 402 billion NOK after costs. This corresponds to average annual active returns of 0.27% before costs, and 0.19% after costs. In the most recent four year period, active management has continued to add value, with mean annual gross and net active returns of 0.24% and 0.20%. These results reflect very low management costs of about 0.04% per year.</p>
</details>
:::

::: {.entry}
[[Industry report]{.entry-org}November 2023]{.entry-meta}

[Return on pension assets]{.entry-title}

[with Andreas Ørpetveit]{.entry-sub}

::: {.entry-links}
[Publisher](https://www.pensjonskontoret.no/rapporter-mv/2023-nhh---avkastning-pa-pensjonsmidlene){.paper-link}
:::
:::
```

- [ ] **Step 2: Render and confirm the page exists**

```bash
QUARTO="/c/Users/s12600/AppData/Local/Programs/Positron/resources/app/quarto/bin/quarto.exe"
"$QUARTO" render
test -f docs/practice/index.html && echo "practice page built"
```

Expected: exit code 0 and `practice page built`.

- [ ] **Step 3: Confirm the reports left Research**

```bash
grep -c "Sovereign Wealth Fund" docs/research/index.html || echo "0 — correctly absent from Research"
grep -c "Sovereign Wealth Fund" docs/practice/index.html
```

Expected: absent from Research, at least `1` in Practice.

- [ ] **Step 4: Commit**

```bash
git add practice/index.qmd
git commit -m "Add Practice page and move the public and industry reports to it"
```

---

### Task 6: Teaching page and the finished navbar

**Files:**
- Create: `teaching/index.qmd`
- Modify: `_quarto.yml` (navbar)

**Interfaces:**
- Consumes: every class from Task 4 unchanged, plus `.page-lead` from Task 2. Adds one new class, `.past-teaching`, for the condensed assistantship list.
- Produces: the final navbar; after this task all five nav destinations resolve.

- [ ] **Step 1: Append the one new rule**

Add to the end of `assets/theme.scss`:

```scss
// Condensed list — earlier teaching assistantships, not full entries.
.past-teaching {
  list-style: none;
  padding: 0;
  margin: var(--sp-3) 0 0;
  max-width: var(--measure);
}

.past-teaching li {
  display: flex;
  justify-content: space-between;
  gap: var(--sp-3);
  padding: var(--sp-2) 0;
  border-bottom: 1px solid var(--rule);
  font-size: var(--fs-sub);
  color: var(--body);
}

.past-teaching li:last-child { border-bottom: 0; }

.past-teaching span {
  font-family: var(--sans);
  font-size: var(--fs-meta);
  font-weight: 500;
  letter-spacing: 0.09em;
  color: var(--muted);
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}
```

- [ ] **Step 2: Create `teaching/index.qmd`**

The two course descriptions are written from the course titles; the owner should confirm the wording at review.

```markdown
---
title: "Teaching"
toc: false
---

[Courses I currently teach at NHH, and what they are actually about.]{.page-lead}

::: {.sect}
## Current courses

[NHH]{.sect-tag}
:::

::: {.entry}
[[FOR21 · BSc]{.entry-org}2024–]{.entry-meta}

[Ownership Management and Private Equity]{.entry-title}

[How private equity owners try to create value — governance, leverage and operational change — and what the evidence says about whether they succeed.]{.entry-sub}
:::

::: {.entry}
[[BED3 · BSc]{.entry-org}2023–]{.entry-meta}

[Capital Budgeting and Finance]{.entry-title}

[The core toolkit for deciding which investments a firm should make: discounting, the cost of capital, and how those decisions hold up under uncertainty.]{.entry-sub}
:::

::: {.sect}
## Earlier teaching

[Assistantships]{.sect-tag}
:::

::: {}
<ul class="past-teaching">
<li>Asset Management (MSc) <span>2019–2021</span></li>
<li>Capital Budgeting (MSc) <span>2020</span></li>
<li>Management Control (MSc) <span>2018–2020</span></li>
<li>Introduction to R (MSc) <span>2018–2020</span></li>
<li>Capital Budgeting and Finance (BSc) <span>2017–2018</span></li>
<li>Empirical Methods (BSc) <span>2017–2018</span></li>
<li>Statistics for Economists (BSc) <span>2016–2018</span></li>
<li>Calculus and Linear Algebra (BSc) <span>2016–2018</span></li>
<li>Mathematics for Economists (BSc) <span>2015–2017</span></li>
<li>Financial Accounting (BSc) <span>2015</span></li>
</ul>
:::
```

- [ ] **Step 3: Finish the navbar**

In `_quarto.yml`, replace the `right:` list under `navbar:` with:

```yaml
    right:
      - text: Home
        aria-label: "Home"
        href: index.qmd
      - text: Research
        aria-label: "Research"
        href: research/index.qmd
      - text: Teaching
        aria-label: "Teaching"
        href: teaching/index.qmd
      - text: Practice
        aria-label: "Practice"
        href: practice/index.qmd
      - text: CV
        aria-label: "CV (PDF)"
        href: assets/Andre_W_Sjuve.pdf
```

- [ ] **Step 4: Render and confirm every nav destination resolves**

```bash
QUARTO="/c/Users/s12600/AppData/Local/Programs/Positron/resources/app/quarto/bin/quarto.exe"
"$QUARTO" render
for f in docs/index.html docs/research/index.html docs/teaching/index.html docs/practice/index.html docs/assets/Andre_W_Sjuve.pdf; do
  test -f "$f" && echo "ok   $f" || echo "MISS $f"
done
```

Expected: five `ok` lines, no `MISS`.

- [ ] **Step 5: Commit**

```bash
git add assets/theme.scss teaching/index.qmd _quarto.yml
git commit -m "Add Teaching page and complete the navbar"
```

---

### Task 7: Selected work on the home page

Closes the dead space below the fold identified in spec §2.

**Files:**
- Modify: `index.qmd` (append)

**Interfaces:**
- Consumes: every class from Task 4 unchanged. Adds no new CSS.
- Produces: nothing later tasks depend on.

- [ ] **Step 1: Append to `index.qmd`**

Add below the closing `:::` of the hero block:

```markdown
::: {.sect}
## Selected work

[Three of five]{.sect-tag}
:::

::: {.entry}
[[Management Science]{.entry-org}September 2025]{.entry-meta}

[Forced to Be Active: Evidence From a Regulation Intervention]{.entry-title}

[with Petter Bjerksund, Trond Døskeland and Andreas Ørpetveit]{.entry-sub}

::: {.entry-links}
[Publisher](https://doi.org/10.1287/mnsc.2023.03124){.paper-link}
[SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3635718){.paper-link}
:::
:::

::: {.entry}
[[Journal of Portfolio Management]{.entry-org}Forthcoming]{.entry-meta}

[Where Active Management Adds Value for a Large Asset Owner]{.entry-title}

[with Trond Døskeland]{.entry-sub}
:::

::: {.entry}
[[Journal of Empirical Finance]{.entry-org}March 2025]{.entry-meta}

[Do Fees Matter? Investor's Sensitivity to Active Management Fees]{.entry-title}

[with Trond Døskeland and Andreas Ørpetveit]{.entry-sub}

::: {.entry-links}
[Publisher](https://doi.org/10.1016/j.jempfin.2025.101596){.paper-link}
[SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3857628){.paper-link}
:::
:::

::: {.entry-links}
[All research](research/index.qmd){.paper-link}
[Curriculum vitae](assets/Andre_W_Sjuve.pdf){.paper-link}
:::
```

- [ ] **Step 2: Render**

```bash
QUARTO="/c/Users/s12600/AppData/Local/Programs/Positron/resources/app/quarto/bin/quarto.exe"
"$QUARTO" render
```

Expected: exit code 0.

- [ ] **Step 3: Verify the home page now fills the viewport**

```bash
cd docs && python -m http.server 8899 --bind 127.0.0.1 &
sleep 2
```

Playwright, one call:

```js
async (page) => {
  await page.setViewportSize({ width: 1280, height: 900 });
  await page.goto('http://127.0.0.1:8899/', { waitUntil: 'networkidle' });
  await page.screenshot({ path: '.playwright-mcp/t7-home-1280.png', fullPage: true, scale: 'css' });
  return await page.evaluate(() => JSON.stringify({
    docHeight: document.documentElement.scrollHeight,
    entries: document.querySelectorAll('.entry').length
  }));
}
```

Expected: `entries` is `3`, and `docHeight` is greater than `900` — the page no longer ends mid-viewport. Read the screenshot and confirm there is no band of empty ground above the footer.

Kill the server.

- [ ] **Step 4: Commit**

```bash
git add index.qmd
git commit -m "Add Selected work to the home page"
```

---

### Task 8: Final verification pass

No new features. Proves the whole site against the spec's §8 and the global constraints, and clears the stale build artifacts left by earlier renders.

**Files:**
- Modify: none expected. Fixes discovered here are made in `assets/theme.scss`.

**Interfaces:**
- Consumes: the finished site.
- Produces: a clean full render and a screenshot set for the owner's review.

- [ ] **Step 1: Clear stale build output and render from scratch**

Earlier renders left orphaned hashed CSS files in `docs/site_libs/`. Remove the whole output directory so the review is of a clean build.

```bash
powershell -c "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Where-Object { \$_.CommandLine -like '*http.server*' } | ForEach-Object { Stop-Process -Id \$_.ProcessId -Force }"
rm -rf docs .quarto
QUARTO="/c/Users/s12600/AppData/Local/Programs/Positron/resources/app/quarto/bin/quarto.exe"
"$QUARTO" render
```

Expected: exit code 0, `docs/` regenerated.

- [ ] **Step 2: Re-run the palette test**

```bash
python _design/tools/check_palette.py
```

Expected: PASS, exit code 0.

- [ ] **Step 3: Assert the no-cards and no-second-breakpoint constraints**

```bash
grep -nE 'border-radius|box-shadow' assets/theme.scss | grep -v ': 0' || echo "no radius or shadow — ok"
grep -c 'min-width: 720px' assets/theme.scss
grep -nE '@media[^{]*(min|max)-width' assets/theme.scss | grep -v '720px' || echo "single breakpoint — ok"
```

Expected: the first and third print their `ok` message; the second prints the number of `720px` queries (3 or 4 is correct — hero, entry, and any added in Task 6).

- [ ] **Step 4: Screenshot every page at both widths**

```bash
cd docs && python -m http.server 8899 --bind 127.0.0.1 &
sleep 2
```

Playwright, one call:

```js
async (page) => {
  const pages = [['home','/'],['research','/research/'],['teaching','/teaching/'],['practice','/practice/']];
  const out = [];
  for (const [name, path] of pages) {
    for (const w of [1280, 480]) {
      await page.setViewportSize({ width: w, height: 900 });
      await page.goto('http://127.0.0.1:8899' + path, { waitUntil: 'networkidle' });
      await page.screenshot({ path: `.playwright-mcp/final-${name}-${w}.png`, fullPage: true, scale: 'css' });
      const overflow = await page.evaluate(() =>
        document.documentElement.scrollWidth > document.documentElement.clientWidth);
      out.push(`${name}@${w} horizontalOverflow=${overflow}`);
    }
  }
  return out.join('\n');
}
```

Expected: `horizontalOverflow=false` on all eight. Any `true` is a bug — find the element wider than its container and give it `overflow-x: auto` or a `min-width: 0`.

- [ ] **Step 5: Check focus visibility and the active nav marker**

Playwright, one call:

```js
async (page) => {
  await page.setViewportSize({ width: 1280, height: 900 });
  await page.goto('http://127.0.0.1:8899/research/', { waitUntil: 'networkidle' });
  await page.keyboard.press('Tab');
  await page.keyboard.press('Tab');
  await page.screenshot({ path: '.playwright-mcp/final-focus.png', scale: 'css' });
  return await page.evaluate(() => {
    const active = document.querySelector('.navbar-nav .nav-link.active, .navbar-nav .nav-link[aria-current]');
    const el = document.activeElement;
    return JSON.stringify({
      focused: el ? el.tagName + ':' + (el.textContent || '').trim().slice(0, 20) : null,
      outline: el ? getComputedStyle(el).outlineColor : null,
      activeNav: active ? active.textContent.trim() : 'NONE'
    });
  });
}
```

Expected: `activeNav` is `Research`; `outline` resolves to the navy `rgb(20, 52, 107)` on the focused element. If `activeNav` is `NONE`, Quarto is not marking the current page — add `aria-current` handling or accept Quarto's `.active` class, whichever the rendered HTML shows.

Kill the server.

- [ ] **Step 6: Send the owner the screenshot set and stop**

Send `final-home-1280.png`, `final-research-1280.png`, `final-teaching-1280.png`, `final-practice-1280.png` and `final-home-480.png` for review.

**Do not push.** The plan ends at the owner's sign-off.

- [ ] **Step 7: Commit the rebuilt output**

```bash
git add -A docs
git commit -m "Rebuild site output on the Bone & Navy design system"
```

---

## Self-Review

**Spec coverage.** §3 colour → Task 1. §4 type → Task 1 (tokens) and Task 3 (gate). §5 space and layout → Tasks 1–2. §6.1 navbar → Tasks 2 and 6. §6.2 hero and page title → Tasks 2 and 3. §6.3 section head, §6.4 entry, §6.5 link, §6.6 disclosure → Task 4. §7 pages: Home Tasks 3 and 7, Research Task 4, Teaching Task 6, Practice Task 5, CV Task 6. §8 accessibility → Task 1 (contrast, focus, reduced motion) and Task 8 (focus and `aria-current` verified). §9 file plan → all tasks. §10 out of scope → nothing in the plan touches it. §11 build and verification → Global Constraints and Task 3's gate.

**Two spec items deliberately not given their own task.** The headshot: the hero as specified is typographic and carries no photograph, so `assets/images/headshot.jpg` is now used only as the favicon — this is a visible change from the current site and is called out for the owner at review. The `--sp-6` token is used only by `main.content` padding; that is correct, not an omission.

**Placeholder scan.** No TBD, no "similar to Task N", no "add error handling". Every code step carries its full content. The two course descriptions in Task 6 are real copy, flagged for the owner's wording review rather than left blank.

**Type consistency.** Class names are identical across tasks: `.hero .hero-meta .hero-name .hero-lead` (Task 3), `.sect .sect-tag .entry .entry-meta .entry-org .entry-title .entry-sub .entry-links .paper-link details.abstract` (Task 4, reused verbatim in 5, 6, 7), `.page-lead` (Task 2, used in 5 and 6), `.past-teaching` (Task 6 only). Token names match §3–5 of the spec exactly. The SCSS variable is `$body-ink` while the custom property is `--body`; this is intentional — `$body` collides with Bootstrap — and the palette test checks `body-ink`, matching the SCSS side.

**One risk the executor must not paper over.** Task 3 Step 4 is a stop-and-report gate, not a checkbox. Spectral on `#FAF9F6` has never been seen. If it reads wrong, the swap to Source Serif 4 is the owner's decision.
