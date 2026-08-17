#!/usr/bin/env python3
"""Generate the Harada Mastery Toolkit from a toolkit.json file.

Standard library only — no packages, no uv, no network. Runs anywhere
Python 3 exists:

    python3 generate_toolkit.py /path/to/toolkit.json

Outputs three files next to the input JSON:
    harada-ow64-grid.html         (open in a browser; print to PDF if wanted)
    daily-routine-checklist.html  (open in a browser; print to PDF if wanted)
    weekly-performance-diary.md

See ../templates/toolkit-example.json for the expected schema.
"""

import html
import json
import sys
from pathlib import Path

# Position order around a center cell: TL, T, TR, L, R, BL, B, BR.
# Pillar N occupies position N in the center block AND its own outer block
# sits at the same position in the 3x3 arrangement of blocks (mandala layout).
RING_POSITIONS = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1), (2, 2)]

PAGE_CSS = """
  :root {
    --navy: #1f4e79; --blue: #9dc3e6; --pale: #f2f7fc; --line: #8faadc;
  }
  * { box-sizing: border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    color: #1a1a1a; margin: 2rem auto; max-width: 1100px; padding: 0 1rem;
  }
  h1 { color: var(--navy); margin-bottom: 0.25rem; }
  .subtitle { color: #555; margin-top: 0; }
  @media print { body { margin: 0.5rem; } .noprint { display: none; } }
"""


def load_toolkit(path: Path) -> dict:
    data = json.loads(path.read_text())
    pillars = data.get("pillars", [])
    if len(pillars) != 8:
        sys.exit(f"error: expected 8 pillars, got {len(pillars)}")
    for i, pillar in enumerate(pillars, 1):
        actions = pillar.get("actions", [])
        if len(actions) != 8:
            sys.exit(f"error: pillar {i} ({pillar.get('name', '?')}) has {len(actions)} actions, expected 8")
    if not data.get("goal"):
        sys.exit("error: missing 'goal'")
    return data


def action_text(action) -> str:
    return action["text"] if isinstance(action, dict) else str(action)


def build_grid_html(data: dict, out: Path) -> None:
    # cells[row][col] -> (text, css_class) for the 9x9 grid
    cells = [[("", "action") for _ in range(9)] for _ in range(9)]
    cells[4][4] = (data["goal"], "goal")
    for idx, (ci, cj) in enumerate(RING_POSITIONS):
        cells[3 + ci][3 + cj] = (data["pillars"][idx]["name"], "pillar")
    for idx, (bi, bj) in enumerate(RING_POSITIONS):
        pillar = data["pillars"][idx]
        cells[bi * 3 + 1][bj * 3 + 1] = (pillar["name"], "pillar")
        for aidx, (ci, cj) in enumerate(RING_POSITIONS):
            cells[bi * 3 + ci][bj * 3 + cj] = (action_text(pillar["actions"][aidx]), "action")

    rows = []
    for r in range(9):
        tds = []
        for c in range(9):
            text, cls = cells[r][c]
            edge = []
            if c % 3 == 0:
                edge.append("bl")
            if c % 3 == 2:
                edge.append("br")
            if r % 3 == 0:
                edge.append("bt")
            if r % 3 == 2:
                edge.append("bb")
            tds.append(f'<td class="{cls} {" ".join(edge)}">{html.escape(text)}</td>')
        rows.append("<tr>" + "".join(tds) + "</tr>")

    out.write_text(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Harada OW64 Grid</title>
<style>
{PAGE_CSS}
  table {{ border-collapse: collapse; width: 100%; table-layout: fixed; }}
  td {{
    border: 1px solid var(--line); padding: 6px; font-size: 11px;
    text-align: center; vertical-align: middle; height: 72px; word-wrap: break-word;
  }}
  td.bl {{ border-left: 2.5px solid var(--navy); }}
  td.br {{ border-right: 2.5px solid var(--navy); }}
  td.bt {{ border-top: 2.5px solid var(--navy); }}
  td.bb {{ border-bottom: 2.5px solid var(--navy); }}
  td.goal {{ background: var(--navy); color: #fff; font-weight: 700; font-size: 13px; }}
  td.pillar {{ background: var(--blue); color: var(--navy); font-weight: 700; font-size: 12px; }}
  td.action {{ background: var(--pale); }}
  @media print {{ td {{ height: 60px; font-size: 9px; }} }}
</style>
</head>
<body>
<h1>Open Window 64</h1>
<p class="subtitle">{html.escape(data["goal"])} &mdash; deadline: {html.escape(str(data.get("deadline", "n/a")))}</p>
<p class="noprint subtitle">Tip: print this page (Cmd+P) and choose "Save as PDF" for a wall copy.</p>
<table>
{chr(10).join(rows)}
</table>
</body>
</html>
""")


def build_checklist_html(data: dict, out: Path) -> None:
    def checkbox_list(items) -> str:
        lis = "".join(f'<li><span class="box"></span>{html.escape(t)}</li>' for t in items)
        return f'<ul class="checks">{lis}</ul>'

    anchors = [
        f"I will {i['action']} at {i['time']} in {i['location']}"
        for i in data.get("when_where", [])
    ]

    weekly: dict[str, list[str]] = {}
    for pillar in data["pillars"]:
        for action in pillar["actions"]:
            if isinstance(action, dict) and action.get("frequency") == "weekly":
                weekly.setdefault(action.get("day", "Unscheduled"), []).append(action["text"])
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday", "Unscheduled"]
    weekly_html = ""
    if weekly:
        weekly_html = "<h2>Weekly Actions (by day)</h2>"
        for day in sorted(weekly, key=lambda d: day_order.index(d) if d in day_order else 99):
            weekly_html += f"<h3>{html.escape(day)}</h3>" + checkbox_list(weekly[day])

    scripts_html = "".join(
        f"<li><strong>If</strong> {html.escape(i['obstacle'])}, "
        f"<strong>then</strong> I will {html.escape(i['response'])}.</li>"
        for i in data.get("if_then", [])
    )

    out.write_text(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Daily Routine Checklist</title>
<style>
{PAGE_CSS}
  body {{ max-width: 760px; }}
  h2 {{ color: var(--navy); border-bottom: 2px solid var(--blue); padding-bottom: 4px; margin-top: 1.8rem; }}
  h3 {{ margin: 0.9rem 0 0.3rem; }}
  ul.checks {{ list-style: none; padding-left: 0; margin: 0.4rem 0; }}
  ul.checks li {{ margin: 0.45rem 0; display: flex; align-items: flex-start; gap: 0.55rem; }}
  .box {{
    display: inline-block; width: 14px; height: 14px; flex: 0 0 14px;
    border: 1.5px solid var(--navy); border-radius: 2px; margin-top: 2px;
  }}
  ol.scripts li {{ margin: 0.6rem 0; }}
</style>
</head>
<body>
<h1>Daily Routine Checklist</h1>
<p class="subtitle">Goal: {html.escape(data["goal"])} &mdash; deadline: {html.escape(str(data.get("deadline", "n/a")))}</p>
<p class="noprint subtitle">Tip: print this page (Cmd+P) and choose "Save as PDF" for a daily paper copy.</p>

<h2>Anchor Habits (When-Where Implementation Intentions)</h2>
{checkbox_list(anchors)}
{weekly_html}
<h2>If-Then Emergency Scripts</h2>
<ol class="scripts">
{scripts_html}
</ol>
</body>
</html>
""")


def build_diary_md(data: dict, out: Path) -> None:
    pillar_names = ", ".join(p["name"] for p in data["pillars"])
    out.write_text(f"""# Weekly Performance Diary

**Goal:** {data['goal']}
**Deadline:** {data.get('deadline', 'n/a')}
**Pillars:** {pillar_names}

Copy the template below for each week. Review the month's entries every four weeks and recalibrate the grid.

---

## Week of ____________

### 1. Spirit (Mindset & Motivation)
- What reconnected me to my "Why" this week?
- Where did motivation dip, and what triggered it?

### 2. Skills (Competence & Craft)
- Which grid actions moved my skills forward?
- What did I learn that I couldn't do last week?

### 3. Physical (Health & Energy)
- How were sleep, exercise, and energy levels?
- Did physical state ever block an anchor habit?

### 4. Daily Life (Routines & Environment)
- Which anchor habits held? Which slipped, and when?
- Did any If-Then script fire? Did it work?

### Scores & Adjustments
- Anchor habit completion: ____ / 7 days
- One action to refine or swap on the grid next week:
- One win to celebrate:
""")


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("usage: python3 generate_toolkit.py /path/to/toolkit.json")
    json_path = Path(sys.argv[1]).expanduser().resolve()
    if not json_path.is_file():
        sys.exit(f"error: {json_path} not found")

    data = load_toolkit(json_path)
    out_dir = json_path.parent

    grid = out_dir / "harada-ow64-grid.html"
    checklist = out_dir / "daily-routine-checklist.html"
    diary = out_dir / "weekly-performance-diary.md"

    build_grid_html(data, grid)
    build_checklist_html(data, checklist)
    build_diary_md(data, diary)

    for path in (grid, checklist, diary):
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
