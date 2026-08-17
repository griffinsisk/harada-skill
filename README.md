# Harada Coach

An agent skill that coaches you through the [Takashi Harada Method](https://theharadamethod.com/) until an ambitious goal is a 64-cell action grid you can hang on the wall.

You write the goal, the eight pillars, and the 64 actions. The skill is a behavioral editor: it blocks vague verbs, insists on frequency and controllability, and compiles the result into printable files.

Works with Claude Code, Cursor, Codex, Copilot, and any other agent that loads [Agent Skills](https://agentskills.io/).

## Install

```bash
npx skills add griffinsisk/harada-skill
```

The [skills CLI](https://github.com/vercel-labs/skills) detects the agents on your machine and installs `harada-coach` into the right skills folder. Add `-g` to install for your user account (every project) instead of the current repo.

Then start a **new chat** and say:

```
Build a Harada chart
```

That’s it. Other triggers that work: “Harada Method”, “OW64 grid”, “Harada coaching”, or “turn this goal into daily controllable behaviors.”

## What to expect

This is a coaching conversation, not a form. Come in with a real goal.

1. **Goal and spirit** — a concrete goal with a deadline, why it matters, and how you usually succeed or fail at goals this size.
2. **Eight pillars** — you propose all eight in your own words. The coach hints 1–2 examples, compares, and you lock them.
3. **64 actions** — eight specific, 100% controllable behaviors per pillar, one pillar at a time. Daily by default; weekly only if you name the day.
4. **Implementation intentions** — 5–10 When-Where anchors (`I will [behavior] at [time] in [location]`) and three If-Then scripts against your failure patterns.
5. **Toolkit** — three files written to `~/Desktop/Harada/`.

The coach will not invent your chart. Vague actions like “study,” “practice,” or “network” get sent back. “Submit 2 customized applications daily” is the bar.

Sessions can span multiple chats. Progress is saved in `~/Desktop/Harada/harada-state.md`; the next session resumes instead of restarting.

Python 3 is the only extra dependency, and only for step 5. The generator uses the standard library — no packages, no network.

## What you walk away with

| File | Use |
|---|---|
| `harada-ow64-grid.html` | Classic 9×9 Open Window 64 layout. Open in a browser; print to PDF for a wall copy. |
| `daily-routine-checklist.html` | Anchor habits with When-Where triggers, weekly actions by day, and three If-Then scripts. Printable checkboxes. |
| `weekly-performance-diary.md` | Weekly reflection on the Four Aspects (Spirit, Skills, Physical, Daily Life). |

A fictional Product Hunt launch example is in [`sample-output/`](sample-output/).

## Regenerating the toolkit

If `toolkit.json` already exists:

```bash
python3 .claude/skills/harada-coach/scripts/generate_toolkit.py ~/Desktop/Harada/toolkit.json
```

Schema: [`scripts/toolkit-example.json`](.claude/skills/harada-coach/scripts/toolkit-example.json). Outputs land next to the input JSON.
