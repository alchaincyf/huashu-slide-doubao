<sub><b>🌐 English</b> · <a href="README.zh.md">中文</a></sub>

<div align="center">

# huashu-slide-doubao

> **Doubao-only AI visual material production skill (seedream 5.0).**
> Say one sentence — get a finished PPT, WeChat cover, or Bilibili/YouTube thumbnail.

[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Doubao Only](https://img.shields.io/badge/Runtime-Doubao%20Only-orange)](https://www.doubao.com)
[![Built-in image_gen](https://img.shields.io/badge/Uses-seedream%205.0%20Pro-blueviolet)](https://www.doubao.com)
[![No API fees](https://img.shields.io/badge/API%20fees-Zero-green)](#why-doubao-only)

</div>

---

## Why Doubao-only?

Most "AI PPT" skills wrap Gemini / OpenAI Image / Nano Banana API calls — every slide costs money. **Doubao has built-in `image_gen` (default: seedream_5.0_pro)**: it's already paid for via your Doubao membership. The whole point of this skill is to use that built-in capability instead of burning a second image API.

If you run this skill in Claude Code, Cursor, or Codex, Doubao's built-in `image_gen` doesn't exist there, and the skill won't work as intended. Use [`huashu-design`](https://github.com/alchaincyf/huashu-design) (HTML-native) or [`huashu-wechat-image`](https://github.com/alchaincyf/huashu-skills) (Gemini-backed) for those runtimes.

## What it does

Four delivery paths, all powered by Doubao's `image_gen` (seedream_5.0_pro):

| Path | Output | Use when |
|---|---|---|
| **Path 1 · AI Image PPT** (default) | PPTX + HTML deck, each slide is a full image | Presentations, course material, pitch decks |
| **Path 2 · HTML Image Deck** | Full-screen web deck (←/→ keys) | Quick preview, web-published decks |
| **Path 3 · Editable HTML → PPTX** | Editable text PPTX | **Only** when user explicitly says "I need editable text" |
| **Path 4 · Single Cover Image** | WeChat / Bilibili / YouTube / Xiaohongshu cover PNG | Article hero images, video thumbnails, marketing posters |

## Quick start

In a Doubao session:

```
Use huashu-slide-doubao to make a 10-page deck about [your topic].
```

That's it. The skill will:

1. Ask 1-3 clarifying questions (audience, tone, format)
2. Recommend 3 differentiated design philosophies (Bloomberg / Field Notes / Pentagram etc.)
3. Run a brand asset protocol if your topic involves a specific brand (downloads logo, product shots, UI screenshots → writes a project-local `brand-spec.md`)
4. Generate slides via `image_gen` (seedream_5.0_pro), curl-download into your project, assemble PPTX + HTML

For a single cover image:

```
Use huashu-slide-doubao to make a WeChat cover for my article about [topic].
```

The skill defaults to **3 differentiated versions** for important single images, so you have real choices instead of "the AI's best guess."

## Install

```bash
cd ~/.agents/skills/  # or your Doubao skills directory
# place the huashu-slide-doubao folder here
```

Or wherever your Doubao skill directory lives.

### Optional: image hosting

If you want to publish results to WeChat or other platforms that need permanent URLs, set up ImgBB:

```bash
cp .env.example .env
# Edit .env and add your free ImgBB key from https://api.imgbb.com
```

The bundled `scripts/upload_image.py` uses Python stdlib only — no `pip install` needed.

## Core mechanics

### 🔴 Default path lock

In Doubao environments, the skill **always defaults to Path 1 (AI Image PPT)**. The two — and only two — triggers for switching to Path 3 (HTML/editable) are:

1. User explicitly says "I want editable PPT" / "don't want image PPT"
2. `image_gen` actually fails to invoke (≥3 times)

The skill includes an explicit list of "forbidden self-justification" patterns to stop the agent from rationalizing away the default. This was added after a real-world failure where an agent talked itself into HTML mode because "the content needs precise version numbers."

### Page types & density tiers

Not every slide should have the same density. The skill enforces 4 page types:

| Type | Text ceiling | Required elements |
|---|---|---|
| Cover (always slide 01) | ≤8 char title + ≤16 char subtitle | Big title + hero visual, no info blocks |
| Section divider | ≤30 chars | 1 strong judgment + 1 visual metaphor |
| Content page (main) | 80-180 chars typical, 220 max | Title + 1-3 sentence explanation + 2-4 labels + visual |
| Conclusion page | ≤40 chars | 1 big judgment + 1 signature visual |

The skill explicitly warns the agent that the ceiling is **not a target** — "the sparse content page is more professional than the stuffed one."

### Brand Asset Protocol

If your topic involves a specific brand (Anthropic, Linear, your own company), the skill runs a 5-step protocol:

1. Ask user for what assets they have (logo / product shots / UI screenshots / brand guidelines)
2. Search official channels (`<brand>.com/brand`, `/press-kit`, press kits, App Store)
3. Download via curl
4. Verify + extract colors (`grep` hex codes from inline CSS)
5. Write project-local `brand-spec.md` + **mandatory user checkpoint** before generating any slides

The protocol exists because cover images / decks without real brand assets become "generic AI tech aesthetic." 30 minutes of asset gathering saves 2 hours of rework.

### Spread Frame + Mascot Continuity

For information-manual style decks (Field Notes × Anthropic, Penguin Books, Bloomberg Businessweek), the skill recommends:

- **Spread Frame**: A consistent 3-element layout across all content pages — top brand bar + free body + bottom conclusion strip. Body layout varies, frame stays.
- **Mascot Continuity**: If your brand has a mascot (a shrimp, a pixel character, an IP figure), have the mascot appear across content pages in different poses — turns a deck from "8 isolated infographics" into "a connected story."

Both patterns are validated by real-world delivery (OpenClaw Orange Paper PPT, 2026-05-23).

### Personal-brand asset injection (swappable)

The skill ships with three example pixel-style assets in `assets/personal-brand/` (`像素风头像.png`, `像素公众号头图示例.png`, `像素品牌资产.png`) — these are the maintainer's (花叔 / @AlchainHust) personal IP assets, included as a working example of the "personal brand auto-inject" pattern.

For your own use, you have two options:

1. **Replace**: Swap in your own logo / avatar / style example PNGs and edit the trigger words in SKILL.md (search for "花叔风格")
2. **Disable**: Delete `assets/personal-brand/` — the skill's main features (slides, single covers, brand asset protocol) all still work

## What's bundled

```
huashu-slide-doubao/
├── SKILL.md                   # Agent instructions (Chinese, but agent is bilingual)
├── test-prompts.json          # 7 test prompts covering all paths
├── assets/personal-brand/     # 3 pixel-style example assets (swappable)
├── references/
│   ├── design-principles.md
│   ├── prompt-templates.md
│   ├── proven-styles-gallery.md
│   ├── proven-styles-snoopy.md
│   └── design-movements.md
└── scripts/
    ├── create_slides.py       # PPTX assembly (python-pptx)
    ├── image_deck_html.py     # HTML deck assembly
    ├── html2pptx.js           # Path 3 HTML → PPTX conversion
    └── upload_image.py        # ImgBB upload (stdlib only)
```

All script references in SKILL.md use a `[SKILL_DIR]/...` placeholder. The skill is fully self-contained — no machine-specific absolute paths.

## Iteration history

This skill went through 8 iteration rounds before this release, most driven by real-world delivery failures and successes. See [`results.tsv` in darwin-skill](https://github.com/alchaincyf/darwin-skill) for the full optimization log. Key learnings:

- **R3 (full_test)**: When pixel-style was triggered but the image model put 花叔 character on a coffee mug instead of as the protagonist — added a "character must appear as scene protagonist" rule.
- **R4 (full_test)**: For important single images, generating 3 differentiated versions × different design philosophies is always worth the extra 2 `image_gen` calls.
- **R6 (full_test)**: AI defaults to filling every slide to the ceiling — added page-type-aware density tiers ("ceiling is not target").
- **R7 (full_test)**: OpenClaw deck validated the Spread Frame + Mascot Continuity patterns.
- **R8 (full_test)**: Agent rationalized switching to HTML mode by claiming "content needs precision" — added the 🔴 default-path-lock rule with explicit forbidden-justification patterns.

## Related skills

- [`huashu-design`](https://github.com/alchaincyf/huashu-design) — HTML-native design skill, works in any runtime
- [`huashu-skills`](https://github.com/alchaincyf/huashu-skills) — Other skills (AI proofreading, topic gen, image generation, etc.)
- [`darwin-skill`](https://github.com/alchaincyf/darwin-skill) — The autonomous optimization framework used to iterate on this skill

## License

MIT — free for personal and commercial use, no authorization required.

## Author

[花叔 · @AlchainHust](https://x.com/AlchainHust) — AI Native Coder, indie developer, ~30 万粉自媒体. Made many AI skills, ships many AI products.
