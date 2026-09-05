# Design system — andresjuve.com

**Date:** 2026-09-05
**Status:** Approved direction, ready for implementation planning
**Supersedes:** `.superpowers/specs/2026-06-13-nordic-redesign-design.md` ("Linen Fjord")

---

## 1. What this is

A token system and component set for André Wattø Sjuve's academic site, replacing an
ad-hoc stylesheet in which colours were variables but every size, space and letter-spacing
was a magic number.

The rule this document exists to enforce: **every colour, size and space on the site comes
from section 3, 4 or 5 and nowhere else.**

### Audience, in priority order

1. **Academic peers and search committees.** The only audience that can reject him. They
   skim for venues. Design must make the venue column readable on its own.
2. **Industry practitioners** — asset managers, pension funds, Ministry of Finance. They
   arrive from a GPFG report and need plain language, not abstracts.
3. **Students and prospective advisees.** They need to learn what he studies and feel able
   to email him.

Press and general public are explicitly not an audience.

### Direction

**Editorial voice on a Swiss grid.** A serif sets all running text, as a journal would;
the layout is a strict two-column grid with a fixed metadata rail, as a timetable would.
The serif answers audiences 2 and 3; the grid answers audience 1.

Typeface pair **Spectral + Archivo**; palette **Bone & Navy**. Both chosen from rendered
specimens rather than description.

### Principles

- **Nothing is a card.** No fills, no shadows, no border radius anywhere. Separation is
  rules and whitespace only. A card says "discrete object"; a publication list is a
  sequence, not a set of objects.
- **Rules carry hierarchy.** A 1px `--ink` rule means "new section". A 1px `--rule`
  hairline means "next item". Those are the only two rules in the system.
- **One accent, two jobs.** Navy appears on things you can click, and on the identifying
  line of the metadata column — the journal, the course code, the institution. Nothing else
  is navy. Colour is therefore information, not decoration.
- **One entry component, three uses.** Papers, courses and engagements are the same
  component with different metadata. This is the main reason the system is small.
- **Prose is a design element.** The hero paragraph and course descriptions are set at a
  reading measure and written in plain language. They are what stop the grid reading cold.

---

## 2. Fixes this must deliver

Problems in the current draft that the system exists to solve:

| Problem | Fix |
|---|---|
| Home page ends at ~55% viewport height, then dead space | Home carries a Selected work section (§7) |
| Section headings quieter than the badges inside cards — inverted hierarchy | Section head gets the strong `--ink` rule; metadata is `--muted` and small |
| Every paper identical in weight | Venue name is the emphasised element, in navy Archivo 600 |
| Eight cards at ~2% contrast against the ground | No cards at all |
| Four social icons at four optical weights | Single text link set in Archivo labels, no icon fonts |
| Spacing values with no logic between them | `--sp-1 … --sp-6`, nothing off-scale |
| Teaching, policy and consulting work invisible outside the CV PDF | Teaching and Practice pages (§7) |

---

## 3. Colour — "Bone & Navy"

Light only. No dark palette ships in this version; see §10.

| Token | Hex | Role | Contrast on `--paper` |
|---|---|---|---|
| `--paper` | `#FAF9F6` | Page ground. Barely-warm white | — |
| `--ink` | `#14161A` | Name, entry titles, section heads, strong rules | 17.4 : 1 |
| `--body` | `#4A4F57` | Running text, coauthor lines | 7.8 : 1 |
| `--muted` | `#676D76` | Metadata column, nav, section tags, labels | 5.0 : 1 |
| `--rule` | `#DDDAD1` | Hairline between entries | non-text |
| `--navy` | `#14346B` | Links, metadata identifying line, current nav item, focus ring | 11.5 : 1 |
| `--navy-line` | `#B9C4DA` | Link underlines only | non-text |

**`--muted` was darkened from the `#868C95` shown in the type study.** At that value it
measured 3.3 : 1, which fails WCAG AA — and it is used for the venue column, the one thing
audience 1 reads. `#676D76` passes at 5.0 : 1 and looks materially the same.

There is deliberately **no surface or card token.** If a future component seems to need
one, that is a signal the component is wrong.

---

## 4. Type

```
Serif   Spectral        400, 400i, 500      running text, titles, name, section heads
Sans    Archivo         500, 600            nav, metadata, section tags, links
```

Loaded from Google Fonts in the SCSS defaults block. Fallbacks are mandatory:

```scss
$serif: "Spectral", Georgia, "Times New Roman", serif;
$sans:  "Archivo", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
```

### Scale

Base `16px`. Sizes in `rem` so browser zoom behaves.

| Token | Value | Line height | Tracking | Used for |
|---|---|---|---|---|
| `--fs-display` | `clamp(2.2rem, 5.2vw, 3.25rem)` | 1.02 | −0.018em | The name. Once per site |
| `--fs-lead` | `1.05rem` | 1.62 | — | Hero paragraph, course descriptions |
| `--fs-section` | `1.12rem` | 1.3 | — | Section heads (Spectral italic 500) |
| `--fs-title` | `1.16rem` | 1.32 | −0.005em | Entry titles |
| `--fs-body` | `1rem` | 1.62 | — | Running text, abstracts |
| `--fs-sub` | `0.95rem` | 1.55 | — | Coauthor lines |
| `--fs-label` | `0.68rem` | 1.6 | +0.13em | Nav, section tags, link buttons |
| `--fs-meta` | `0.68rem` | 1.6 | +0.09em | Metadata column |

Weights: Spectral 400 for body and the display name (at that size weight is unnecessary),
500 for titles, section heads and the brand; Archivo 500 for labels, 600 for venue names.

Uppercase is used only for `--fs-label` and `--fs-meta`, always with tracking.

`font-variant-numeric: tabular-nums` on the metadata column so year digits align down the
page.

---

## 5. Space and layout

| Token | Value | Used for |
|---|---|---|
| `--sp-1` | `0.25rem` | Gap between title and subtitle |
| `--sp-2` | `0.5rem` | Gap inside a label group |
| `--sp-3` | `1rem` | Entry internal padding |
| `--sp-4` | `1.5rem` | Between entries |
| `--sp-5` | `2.25rem` | Above a section head |
| `--sp-6` | `3.5rem` | Page-level block separation |
| `--measure` | `54ch` | Max width of any running text |
| `--col-meta` | `9rem` | Fixed metadata column |
| `--gutter` | `2.75rem` | Metadata → content gap |
| `--page-max` | `46rem` | Content container |
| `--bp` | `720px` | Single breakpoint |

Below `--bp` the two-column grid collapses to one column, metadata above content. There is
one breakpoint; a second would mean the grid is wrong.

Layout uses `grid` and `gap` throughout — never per-element margins that collapse.

---

## 6. Components

Six, and no more without a decision to extend this document.

### 6.1 Navbar
Brand left in Spectral italic 500 (`André Wattø Sjuve`, full name, not initials). Links
right in Archivo `--fs-label`, uppercase. 1px `--ink` bottom rule. Current page in `--navy`
with a 1px navy underline and `aria-current="page"`.

### 6.2 Hero and page title
One component, two variants, both on the same `--col-meta` + `--gutter` grid so every page
opens on the same left edge.

- **Hero** (home only). Left: role, institution, city, stacked, in `--fs-meta`. Right: name
  at `--fs-display`, then one lead paragraph at `--fs-lead` constrained to `--measure`.
- **Page title** (Research, Teaching, Practice). Left column empty. Right: the page name at
  `--fs-display` scaled down one step (`clamp(1.9rem, 4vw, 2.5rem)`), optionally followed by
  a single orienting sentence at `--fs-lead`.

1px `--rule` beneath, both variants. Quarto renders front-matter `title:` as the page `h1`;
the SCSS styles that `h1` as the page-title variant rather than introducing a second
mechanism.

### 6.3 Section head
Flex, baseline-aligned. Left: Spectral italic 500 at `--fs-section`. Right: an Archivo
label giving a count or qualifier ("Peer reviewed", "Selected", "NHH"). 1px `--ink` rule
beneath. `--sp-5` above.

### 6.4 Entry — the core component
Two-column grid matching the hero.

- **Metadata column:** primary line in Archivo 600 `--navy` uppercase, secondary line in
  `--muted`. Tabular numerals.
- **Content column:** title at `--fs-title` in `--ink`; subtitle at `--fs-sub` in `--body`;
  optional link row; optional abstract disclosure.
- 1px `--rule` beneath. Last child in a list drops the rule.

Three uses, one implementation:

| Use | Metadata primary | Metadata secondary | Subtitle |
|---|---|---|---|
| Publication | `MANAGEMENT SCIENCE` | `2025` | coauthors |
| Course | `FOR21 · BSc` | `2024–` | what the course is, in plain language |
| Engagement | `MINISTRY OF FINANCE` | `2025` | what the role was |

### 6.5 Link
Archivo `--fs-label`, uppercase, `--navy`, with a 1px `--navy-line` bottom border and
`padding-bottom: 1px` to hold it off the baseline. Not a button — no box, no fill, no
radius. Set in a flex row with `--sp-3` gaps. On hover the border takes `--navy`.

### 6.6 Abstract disclosure
Native `<details>`/`<summary>`. Summary in Archivo `--fs-label`, `--muted`. Body at
`--fs-body` constrained to `--measure`. Native element, so keyboard and screen-reader
behaviour is free.

Footer: existing Quarto footer, `--muted`, `--fs-sub`, 1px `--rule` above.

---

## 7. Pages

| Page | Contains |
|---|---|
| **Home** | Hero · Selected work (3 publication entries: *Management Science*, *JPM* forthcoming, *JEF*) · one link to full research |
| **Research** | Published & forthcoming · Manuscripts being prepared |
| **Teaching** | BED3 · FOR21, each with a plain-language description · earlier teaching assistantships as a condensed list |
| **Practice** | Ministry of Finance GPFG committee · Magma subject editorship · KLP · Norsk legemiddelforsikring · Pension Office · the GPFG and pension reports |
| **CV** | PDF in nav, unchanged |

**Two content moves, flagged for objection:**

1. *Other writings* — the GPFG government report and the pension industry report — moves
   from Research to **Practice**. Research becomes purely peer-reviewed and academic, which
   is what audience 1 expects; the reports serve audience 2 and are stronger next to the
   Ministry of Finance work.
2. **Home gains a Selected work section.** Previously requested scope was hero-only, but a
   hero-only home page is what produces the dead space in §2.

Work-in-progress papers stay off the site, as decided.

---

## 8. Accessibility

- Every text colour meets WCAG AA on `--paper`; ratios recorded in §3.
- Focus: `2px solid var(--navy)`, `outline-offset: 3px`. Never removed.
- Venue emphasis is carried by colour **and** weight **and** position, never colour alone.
- `aria-current="page"` on the active nav item.
- Abstracts use native `<details>`; no custom disclosure JS.
- No motion in the system. `prefers-reduced-motion` guard included regardless.
- Headshot needs a real `alt`; decorative rules are CSS, never `<img>`.

---

## 9. File plan

**Rewrite**
- `assets/theme.scss` — the single source of truth. `scss:defaults` holds §3–5 as variables
  and Bootstrap mappings; `scss:rules` holds §6. No other stylesheet exists.
- `_quarto.yml` — add Teaching and Practice to the navbar.
- `index.qmd` — hero + selected work.
- `research/index.qmd` — reports removed, moved to Practice.

**Create**
- `teaching/index.qmd`
- `practice/index.qmd`

**Content authoring model:** every entry is a Quarto fenced div. Adding a paper means
copying one block and editing four lines of text. No partials, no Lua filters, no listing
metadata — the site is small enough that plain divs are the maintainable choice.

---

## 10. Out of scope

Dark mode (tokens are written so a sibling palette can be added later without touching
components); HTML CV page; blog or listing system; search tuning; analytics; contact form;
logo redesign; work-in-progress publication list; icon fonts.

---

## 11. Build and verification

Quarto is **not on PATH**. Use the Positron bundle:

```
C:\Users\s12600\AppData\Local\Programs\Positron\resources\app\quarto\bin\quarto.exe render
```

Kill any local server serving `docs/` first — Quarto deletes and recreates that directory
and will fail with `os error 32` otherwise.

There are no unit tests. Each step is verified by a clean render plus a screenshot at
1280px and at 480px.

**First implementation step is a verification, not a build:** render the hero and two
publication entries in Spectral on `--paper` and confirm the pairing holds. The type study
showed Spectral on cream and bone with Source Serif, never Spectral on bone. The contrast
maths is sound but the texture has not been seen.

No commits until the rendered site is reviewed and approved.
