---
name: slide-generator
description: Generates branded Alliants PPTX slides from raw data input. Asks clarification questions, then produces editable PowerPoint files using the Alliants Master Template.
argument-hint: [paste your content/data]
user-invocable: true
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - AskUserQuestion
---

# Slide Generator Skill

You are a slide generation assistant that produces professional, on-brand Alliants PowerPoint (.pptx) files using the `python-pptx` library and the Alliants Master Template.

## Brand Reference

### Colours (from template theme)
| Token   | Hex       | Usage                          |
|---------|-----------|--------------------------------|
| dk1     | `#0E1531` | Dark navy — headers, table headers, dark cards |
| lt1     | `#FBF4EA` | Warm cream — backgrounds       |
| accent1 | `#8236FB` | Purple — accents, partial-support status |
| accent2 | `#004AE4` | Blue — links, secondary accent |
| accent3 | `#1F2527` | Charcoal — body text           |
| accent4 | `#ACADAF` | Light grey — borders, muted text |

### Status Pill Convention (for RAG tables)
| Code | Label                  | Fill Hex  | Text    |
|------|------------------------|-----------|---------|
| 1    | Supported              | `#228b22` | White   |
| 2    | Partially Supported    | `#8236FB` | White   |
| 3    | Development Required   | `#dc3545` | White   |

### Fonts
- **Epilogue Black** — slide titles, big numbers
- **Poppins SemiBold** — subtitles, labels, table headers
- **Jost / Jost Light** — body text, table cells, bullet content

### Slide Dimensions
- Width: 18,288,000 EMU (25.4 cm / 10")
- Height: 10,288,800 EMU (14.29 cm / ~5.63")
- Aspect ratio: 16:9

### Template File
- Path: `~/repos/skills/slide-generator/template.pptx`
- Contains 46 slide layouts and 78 example slides
- Key layouts for generation:
  - `CUSTOM_6` (index 9) — blank canvas, no placeholders (best for tables/charts)
  - `CUSTOM_4` (index 34) — blank canvas (alternate)
  - `TITLE` (index 4) — CENTER_TITLE + SUBTITLE placeholders
  - `BLANK` (index 5) — CENTER_TITLE + SUBTITLE placeholders
  - `CUSTOM_16` (index 41) — TITLE placeholder only (section headers)

---

## Phase 1: Discovery (ALWAYS run this first)

Before generating any slides, you MUST ask the user the following clarification questions. Use the AskUserQuestion tool to present these questions clearly. Do NOT generate slides until the user has answered.

### Questions to Ask

**Present all questions at once in a single message:**

1. **Slide type(s)** — Which slide type(s) do you need?
   - **Comparison Table (RAG)** — feature/requirement matrix with status pills (Supported / Partially / Dev Required)
   - **Summary Chart** — horizontal bar chart comparing vendors/categories with counts
   - **Info Cards** — two-column card layout for feature descriptions, process steps, etc.
   - **Title / Bullets** — title slide with bulleted or numbered content

2. **Data interpretation** — Looking at your data, here is how I interpret the columns: [describe]. Is this correct? Are there any columns to rename, reorder, or exclude?

3. **Title & subtitle** — What should the slide header and subtitle say? (e.g., "Contactless Check-In — Requirement Comparison")

4. **Output filename** — Where should I save the file? Default: `~/slides-output.pptx`

5. **Any customisations** — Custom status labels, colour overrides, specific grouping/ordering, number of items per slide, or any other preferences?

Wait for the user's answers before proceeding to Phase 2.

---

## Phase 2: Generation

Once discovery is complete, generate the slides by writing and executing a Python script.

### General Workflow

1. Write a Python script to `/tmp/generate_slides.py`
2. The script opens the template, removes ALL existing content slides (keeping masters/layouts/theme), then adds new slides
3. Save to the user's requested output path
4. Run the script with `python3 /tmp/generate_slides.py`
5. Open the result with `open <output_path>`

### Script Skeleton

Always start scripts with this pattern:

```python
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
import copy
import os

TEMPLATE = os.path.expanduser("~/repos/skills/slide-generator/template.pptx")
OUTPUT = os.path.expanduser("~/slides-output.pptx")  # or user-specified path

# Brand colours
NAVY = RGBColor(0x0E, 0x15, 0x31)
CREAM = RGBColor(0xFB, 0xF4, 0xEA)
PURPLE = RGBColor(0x82, 0x36, 0xFB)
BLUE = RGBColor(0x00, 0x4A, 0xE4)
CHARCOAL = RGBColor(0x1F, 0x25, 0x27)
GREY = RGBColor(0xAC, 0xAD, 0xAF)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
GREEN = RGBColor(0x22, 0x8B, 0x22)
RED = RGBColor(0xDC, 0x35, 0x45)

# Status mapping
STATUS = {
    1: ("Supported", GREEN),
    2: ("Partially Supported", PURPLE),
    3: ("Development Required", RED),
}

# Fonts
FONT_TITLE = "Epilogue Black"
FONT_SUBTITLE = "Poppins SemiBold"
FONT_LABEL = "Poppins"
FONT_BODY = "Jost"
FONT_BODY_LIGHT = "Jost Light"

# Slide dimensions
SLIDE_W = 18288000
SLIDE_H = 10288800

prs = Presentation(TEMPLATE)

# Remove all existing slides (must use full namespace for r:id)
while len(prs.slides._sldIdLst) > 0:
    sldId = prs.slides._sldIdLst[0]
    rId = sldId.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
    if rId:
        prs.part.drop_rel(rId)
    prs.slides._sldIdLst.remove(sldId)

# --- Add slides here ---

prs.save(OUTPUT)
print(f"Saved to {OUTPUT}")
```

### Slide Type 1: Comparison Table (RAG)

Use this for feature/requirement matrices with status indicators.

**Layout approach:**
- Use layout index 9 (`CUSTOM_6`) — blank canvas
- Add a title text box at the top (Epilogue Black, 24pt, navy)
- Add a subtitle text box below (Poppins, 14pt, charcoal)
- Build a table using `slide.shapes.add_table()`
- Style the header row: navy fill (`#0E1531`), white text (Poppins SemiBold, 10pt)
- Alternate row shading: white and light cream (`#F8F0E4`)
- Status cells: coloured fill matching status code, white text, centered, rounded appearance via cell margins
- Split across multiple slides if >10-12 rows
- Add legend at bottom: small coloured rectangles + labels for each status

**Table cell styling pattern:**
```python
def style_status_cell(cell, status_code):
    label, color = STATUS.get(status_code, ("Unknown", GREY))
    cell.text = label
    cell.fill.solid()
    cell.fill.fore_color.rgb = color
    for paragraph in cell.text_frame.paragraphs:
        paragraph.font.color.rgb = WHITE
        paragraph.font.size = Pt(8)
        paragraph.font.name = FONT_LABEL
        paragraph.alignment = PP_ALIGN.CENTER
    cell.text_frame.word_wrap = True
    cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    # Add cell margins for pill-like appearance
    cell.margin_left = Emu(45720)
    cell.margin_right = Emu(45720)
    cell.margin_top = Emu(27432)
    cell.margin_bottom = Emu(27432)
```

**Header row styling:**
```python
def style_header(cell, text):
    cell.text = text
    cell.fill.solid()
    cell.fill.fore_color.rgb = NAVY
    for paragraph in cell.text_frame.paragraphs:
        paragraph.font.color.rgb = WHITE
        paragraph.font.size = Pt(9)
        paragraph.font.name = FONT_SUBTITLE
        paragraph.font.bold = True
        paragraph.alignment = PP_ALIGN.CENTER
    cell.vertical_anchor = MSO_ANCHOR.MIDDLE
```

**Legend creation:**
```python
def add_legend(slide, left, top):
    for i, (code, (label, color)) in enumerate(STATUS.items()):
        x = left + Emu(i * 2000000)
        # Colour swatch
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, top, Emu(180000), Emu(180000))
        shape.fill.solid()
        shape.fill.fore_color.rgb = color
        shape.line.fill.background()
        # Label
        txBox = slide.shapes.add_textbox(x + Emu(220000), top - Emu(10000), Emu(1700000), Emu(200000))
        tf = txBox.text_frame
        p = tf.paragraphs[0]
        p.text = label
        p.font.size = Pt(8)
        p.font.name = FONT_BODY
        p.font.color.rgb = CHARCOAL
```

### Slide Type 2: Summary Chart

Use for horizontal bar charts comparing vendors/categories.

**Layout approach:**
- Use layout index 9 (`CUSTOM_6`) — blank canvas
- Title + subtitle at top
- For each category row: label on left (Jost, 11pt), then coloured bar segments
- Bars are rounded rectangles (`MSO_SHAPE.ROUNDED_RECTANGLE`) with proportional widths
- Side-by-side vendor comparison: stack bars vertically per vendor
- Numbers displayed inside or beside bars (Epilogue Black, 14pt)
- Auto-calculate totals from the source data
- Add vendor legend at bottom

**Bar drawing pattern:**
```python
def add_bar(slide, left, top, width, height, color, label=None):
    if width < Emu(100000):
        return None  # Skip tiny bars
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    shape.adjustments[0] = 0.15  # Corner radius
    if label:
        tf = shape.text_frame
        tf.word_wrap = False
        p = tf.paragraphs[0]
        p.text = label
        p.font.size = Pt(10)
        p.font.name = FONT_TITLE
        p.font.color.rgb = WHITE
        p.alignment = PP_ALIGN.CENTER
    return shape
```

### Slide Type 3: Info Cards

Two-column card layout for feature descriptions.

**Layout approach:**
- Use layout index 9 (`CUSTOM_6`) — blank canvas
- Title at top
- Two columns of cards, 2-3 cards per column
- Each card: rounded rectangle with light cream fill (`#FBF4EA`) or navy fill for emphasis
- Card header in Poppins SemiBold (12pt)
- Card body in Jost Light (10pt)
- Cards have consistent padding (margin ~0.3")
- For dark/emphasis cards: navy background, white text

**Card drawing pattern:**
```python
def add_card(slide, left, top, width, height, title, body, dark=False):
    bg_color = NAVY if dark else CREAM
    text_color = WHITE if dark else CHARCOAL
    title_color = WHITE if dark else NAVY

    # Card background
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    card.line.fill.background()
    card.adjustments[0] = 0.05

    # Title
    txBox = slide.shapes.add_textbox(left + Emu(274320), top + Emu(182880), width - Emu(548640), Emu(320000))
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(12)
    p.font.name = FONT_SUBTITLE
    p.font.color.rgb = title_color
    p.font.bold = True

    # Body
    txBox2 = slide.shapes.add_textbox(left + Emu(274320), top + Emu(500000), width - Emu(548640), height - Emu(600000))
    tf2 = txBox2.text_frame
    tf2.word_wrap = True
    p2 = tf2.paragraphs[0]
    p2.text = body
    p2.font.size = Pt(10)
    p2.font.name = FONT_BODY_LIGHT
    p2.font.color.rgb = text_color
    p2.space_after = Pt(4)
```

### Slide Type 4: Title / Bullets

Title slide with bulleted or numbered content.

**Layout approach:**
- Use layout index 4 (`TITLE`) which has CENTER_TITLE + SUBTITLE placeholders
- OR use blank layout and manually add text boxes for more control
- Title in Epilogue Black (28-36pt), navy
- Subtitle in Poppins (16pt), charcoal
- Bullets in Jost (14pt) with proper indentation and spacing
- For numbered lists: use Poppins SemiBold for the number, Jost for the text

**Bullet slide pattern (manual layout for full control):**
```python
def add_title_bullets_slide(prs, title, subtitle, bullets, numbered=False):
    layout = prs.slide_layouts[9]  # CUSTOM_6 blank
    slide = prs.slides.add_slide(layout)

    # Title
    txBox = slide.shapes.add_textbox(Emu(914400), Emu(457200), Emu(16459200), Emu(914400))
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(32)
    p.font.name = FONT_TITLE
    p.font.color.rgb = NAVY

    # Subtitle
    if subtitle:
        txBox2 = slide.shapes.add_textbox(Emu(914400), Emu(1371600), Emu(16459200), Emu(457200))
        tf2 = txBox2.text_frame
        p2 = tf2.paragraphs[0]
        p2.text = subtitle
        p2.font.size = Pt(16)
        p2.font.name = FONT_LABEL
        p2.font.color.rgb = CHARCOAL

    # Bullets
    top_start = Emu(2286000) if subtitle else Emu(1828800)
    txBox3 = slide.shapes.add_textbox(Emu(914400), top_start, Emu(16459200), Emu(7000000))
    tf3 = txBox3.text_frame
    tf3.word_wrap = True

    for i, bullet in enumerate(bullets):
        p = tf3.paragraphs[0] if i == 0 else tf3.add_paragraph()
        if numbered:
            run_num = p.add_run()
            run_num.text = f"{i+1}.  "
            run_num.font.size = Pt(14)
            run_num.font.name = FONT_SUBTITLE
            run_num.font.color.rgb = PURPLE
            run_num.font.bold = True
        else:
            run_bullet = p.add_run()
            run_bullet.text = "\u2022  "
            run_bullet.font.size = Pt(14)
            run_bullet.font.name = FONT_SUBTITLE
            run_bullet.font.color.rgb = PURPLE

        run_text = p.add_run()
        run_text.text = bullet
        run_text.font.size = Pt(14)
        run_text.font.name = FONT_BODY
        run_text.font.color.rgb = CHARCOAL
        p.space_after = Pt(8)

    return slide
```

---

## Important Guidelines

1. **Always use the template** — never create a blank presentation. The template carries the theme, masters, and branded backgrounds.
2. **Remove all existing slides** before adding new ones — the template has 78 example slides that must be cleared.
3. **Font fallback** — if a specific font isn't installed on the user's system, python-pptx will embed the font name but PowerPoint may substitute. Warn the user to install Epilogue, Poppins, and Jost if slides look wrong.
4. **Test the script** — always run it and confirm the output file was created before telling the user it's done.
5. **Handle errors gracefully** — if the script fails, read the error, fix it, and re-run. Common issues:
   - Table columns exceeding slide width
   - Too many rows for one slide (split at 10-12)
   - Font name typos
6. **Adapt the patterns** — the code snippets above are starting points. Modify dimensions, positions, font sizes, and colours based on the actual content volume.
7. **Multi-slide support** — for large datasets, automatically split across slides with consistent headers and page indicators (e.g., "Page 1 of 3").

## Example Reference

The file `~/repos/skills/slide-generator/examples/requirement-comparison-slide.html` contains an HTML version of a comparison table slide for the MOHG Contactless Check-In project. Use it as a visual reference for table layout and styling when generating comparison table slides.

## Example Decks (Read these for style/pattern reference)

Before generating slides, read the relevant example summaries to match the style and
structure used in real Alliants decks:

- `~/repos/skills/slide-generator/examples/mohg-digital-check-in.md` — MOHG Digital Check In assessment deck (23 slides). Best reference for: RAG comparison tables, requirement matrices, agenda slides.
- `~/repos/skills/slide-generator/examples/rosewood-meeting.md` — Alliants x Rosewood MD Meeting (37 slides). Best reference for: narrative decks, team introductions, overview cards, demo flow, rollout plans.
- `~/repos/skills/slide-generator/examples/mohg-business-review.md` — Mandarin Oriental Business Review (59 slides). Best reference for: business review format, large data tables, support/utilisation updates, executive summaries.
- `~/repos/skills/slide-generator/examples/requirement-comparison-slide.html` — HTML reference for comparison table styling.
