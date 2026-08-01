# fdesign

**AI prototypes degrade with every iteration. fdesign is the missing quality loop that keeps your Agent honest. An open-source alternative to Figma Make and Google Stitch.**

[![PyPI version](https://img.shields.io/pypi/v/fdesign?style=for-the-badge)](https://pypi.org/project/fdesign/)
[![Python](https://img.shields.io/pypi/pyversions/fdesign?style=for-the-badge)](https://pypi.org/project/fdesign/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue?style=for-the-badge)](LICENSE)
[![Agents](https://img.shields.io/badge/agents-7%20supported-green?style=for-the-badge)](#supported-agents)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen?style=for-the-badge)](#)

---

## The Problem: The "Disposable Prototype" Trap

Building a UI with AI (Cursor, Claude, Copilot) always starts out feeling like magic. But as you iterate, that magic quickly turns into a mess. 

Because AI lacks design discipline, it hallucinates new colors, forgets your component library, and injects messy inline styles. What you hoped would be a maintainable project becomes a **disposable prototype**—a tangled codebase that you'll inevitably have to throw away and rewrite from scratch.

**Why does this happen?** AI is perfectly optimized to generate code *forward*, but has zero ability to enforce consistency *backward*. It's exactly like writing code without tests: it works on day one, but silently degrades with every new feature.

```text
WITHOUT fdesign

  Iteration 1:  "Build a login page"  → looks perfect ✓
  Iteration 3:  "Add a dashboard"     → hallucinates new shades of blue, adds inline CSS
  Iteration 5:  "Add settings page"   → forgets components entirely, writes raw HTML
  Iteration 8:  "Change brand color"  → updates 2 files, misses 6 others
  Iteration 10: "Add onboarding"      → unmaintainable Frankenstein codebase

  Result: The AI only generated forward. No one caught the regressions.
```

```text
WITH fdesign

  Iteration 1:  "Build a login page"  → tokens.css + components.js, validated ✓
  Iteration 3:  "Add a dashboard"     → perfectly reuses the exact same tokens and components ✓
  Iteration 5:  "Add settings page"   → fdesign catches raw tags, forces agent to rewrite them ✓
  Iteration 8:  "Change brand color"  → update one token, rebuild — all 8 pages sync ✓
  Iteration 10: "Add onboarding"      → pristine consistency, production-ready ✓

  Result: The quality loop catches what the AI misses. Every page, every iteration.
```

---

## What fdesign Does

fdesign forces your AI to stop writing free-form, disposable HTML and start building a structured, reusable design system. It overrides the AI's default "just generate" behavior by locking it into a strict, backward-checked workflow.

Instead of generating page layouts immediately, the AI must explicitly define design tokens and components first. Then, fdesign acts as your project's quality gate, catching regressions (like bare HTML tags or hallucinatory colors) when the AI inevitably tries to cut corners.

```mermaid
flowchart TD
    Start(["New Iteration / Request"]) --> Sketch["Step 1: Sketch & Plan"]
    
    subgraph "✅ Forward Validation (Building it right)"
        Sketch --> Token["Step 2: Update Tokens"]
        Token -.->|"fdesign token validate"| Token
        Token --> Sitemap["Step 3: Update Sitemap"]
        Sitemap --> Component["Step 4: Update Components"]
        Component -.->|"fdesign component validate"| Component
    end
    
    Component --> Build["Step 5: Build HTML"]
    
    subgraph "🔁 Backward Check (Did the AI miss anything?)"
        Build --> Check{"Step 6: fdesign journey check"}
    end
    
    Check -.->|"❌ Fails: Bare tags, missing references"| Token
    Check -->|"✅ Passes: 100% consistent"| Confirm(["Step 7: User Confirm"])
    Confirm --> Start

    style Check fill:#ffe6e6,stroke:#ff6b6b,stroke-width:2px
```

---

## Why fdesign

### For Individuals (Makers & Founders)
> AI delivers infinite speed, but **you** need sustainable assets.

AI accelerates your imagination, but if you don't enforce discipline, you end up with an unmaintainable toy. fdesign acts as your automated safety net, ensuring your fast prototypes remain structurally sound, preventing technical debt from forcing a complete rewrite.

### For Teams (Designers & Developers)
> Real projects run on design systems, not inline styles.

AI-generated code is notoriously hard to hand off because it relies on hallucinated DOM structures and hardcoded colors. By enforcing W3C DTCG tokens and a strict component YAML, fdesign guarantees the AI outputs developer-ready `tokens.css` and `components.js` that seamlessly merge into real production codebases.


---

## Use Cases

### Scenario 1: The Global Redesign
**Problem:** "Make all the primary buttons slightly rounder, and change the brand color to purple." The AI updates the homepage perfectly, but forgets the dashboard, settings, and login pages.

**fdesign Solution:** The AI is instructed to update the `global.tokens.json`. You run `fdesign token view` to regenerate `tokens.css`. Every single page across the entire project updates instantly with mathematical consistency. No manual sweeping required.

### Scenario 2: The Multi-Page Hallucination
**Problem:** When you ask the AI to build a list view for page 2, it invents a totally new card style with hardcoded `border-radius: 8px` and `#333` hex colors.

**fdesign Solution:** The AI is strictly bound by `.fdesign/components.yaml`. When it attempts to build page 2, `fdesign journey check` detects the bare `<div>` tags and inline styles. The check fails, and the agent is forced to rewrite the page using the registered `DataCard` component or fail the build.

### Scenario 3: Handoff to Engineering
**Problem:** Developers refuse to touch AI prototypes because they're a tangled mess of arbitrary class names and unmaintainable inline styles.

**fdesign Solution:** Because fdesign enforced standard `tokens.css` and documented `components.js` from day one, engineers can drop these exact artifacts directly into their React/Vue/Tailwind design systems. It's production-ready CSS architecture from the start.



---

## Features

- **Design System Tokens**: Manage brand variables using the W3C DTCG format (global → semantic → component).
- **Structured Prototypes**: Compose layouts through defined components, domain logic, and journey maps.
- **Multiple Platform Preview**: Inspect your UI seamlessly across Web, Tablet, and Mobile device shells.
- **Code-Level Output**: Automatically compile design concepts into developer-friendly `tokens.css` and `components.js`.
- **Multi-Version Snapshots**: Save named iterations (v1, v2) and easily compare or roll back versions in the local preview.

### Platform-aware prototype setup

On the first design interaction without an fdesign project, the installed Agent asks for the target platform before generating artifacts:

- **Web** — whether responsive behavior is required and which widths to review. fdesign produces responsive journey HTML and lets you inspect it in phone, tablet, and desktop preview frames.
- **Mobile** — iOS, Android, both, or another device target; then a design direction: `neutral-brand`, `platform-native`, or a named custom system. The Agent models navigation stacks, back/dismiss behavior, overlays, touch-first controls, safe areas, and phone-oriented screen layouts.

`platform-native` resolves a single iOS target to Apple-native/SwiftUI conventions and a single Android target to Google Material 3. For a shared iOS-and-Android prototype, `neutral-brand` derives a consistent UI from the product's design tokens; native output uses separate variants rather than mixing both platforms in one screen. Mobile pages remain ordinary responsive HTML, while fdesign preview supplies the phone/tablet/desktop device frame.

The platform design guidance follows [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/) and [Material 3](https://developer.android.com/develop/ui/compose/designsystems/material3).

### Web support

Web projects can opt into responsive design during discovery. The Agent records that decision in the PRD, designs for the agreed breakpoints, and reviews the same journey in fdesign's phone, tablet, and desktop frames. The generated page remains normal HTML/CSS, so it can be handed off without an artificial device shell embedded in the page.

### Mobile support

Mobile projects can target iOS, Android, or both:

- **iOS native** — Apple HIG and SwiftUI-aligned navigation, tabs, sheets, and action patterns.
- **Android native** — Material 3 components, navigation, dialogs, and bottom sheets.
- **Neutral brand** — a shared token-driven language for cross-platform products, without blending recognizably iOS and Android patterns on one screen.

The preview shell provides device framing; generated journey pages stay focused on real app UI and work as responsive HTML.

### Prototype localization (i18n)

For a new project, fdesign confirms platform and core product requirements, then asks whether localization is needed before project and PRD creation. When enabled, it records a source language and supported language set. Preview supplies the default language selector; fdesign does not add a product-level language setting unless you explicitly request one.

Initialize and manage catalogs through the CLI rather than by manually creating files:

```bash
fdesign locale init --source en
fdesign locale add fr_FR
fdesign locale list
fdesign locale validate
fdesign locale remove fr_FR
```

Catalogs live in `.fdesign/projects/<project>/build/locale/` as one flat Lokalise-compatible JSON map per language:

```json
{
  "checkout.submit": "Place order",
  "checkout.items": "{0} items"
}
```

Journey HTML keeps source copy as a fallback and marks localized text with `data-i18n` (or attributes with `data-i18n-attr`). When `build/locale/` contains valid catalogs, fdesign preview adds a language selector and updates the active prototype. Ask the Agent to add or remove a language at any iteration; it uses the locale CLI, maintains key and placeholder parity, and validates the catalogs before delivery. `fdesign prototype validate` also runs locale validation whenever locale catalogs exist.

### Highlights: The Quality Mechanisms

To keep the AI in check, fdesign enforces a structured workflow combining manual confirmation with two automated quality gates.

- **🫂 Human in the Loop**: The AI never commits blindly. Every iteration pauses for your explicit review and confirmation.
- **✅ Forward Validate**: Verifies tokens and components format and cross-references *before* the AI is allowed to build the page layout (`fdesign token validate`).
- **🔁 Backward Check**: Scans the generated HTML to catch bare DOM tags, hallucinated inline CSS, or missing token references *after* the page is built (`fdesign journey check`).

### Supported Agents

| Agent | Command |
|-------|---------|
| GitHub Copilot | `fdesign enable copilot` |
| Cursor | `fdesign enable cursor` |
| Claude Code | `fdesign enable claude` |
| Trae IDE | `fdesign enable trae` |
| Codex | `fdesign enable codex` |
| Qwen Code | `fdesign enable qwen-code` |
| OpenCode | `fdesign enable opencode` |
| OpenClaw | `fdesign enable openclaw` |

---

## Installation

```bash
pip install fdesign
```

Verify:

```bash
fdesign --version
```

---

## Quick Start

```bash
# 1. Initialize workspace
cd your-project
fdesign init

# 2. Create a project
fdesign project create my-app

# 3. Install skills into your AI agent
fdesign enable copilot     # or: cursor, claude, trae, qwen-code, opencode, openclaw

# 4. Prompt your AI Agent
# Just tell it what you want to build (e.g., "Build a SaaS dashboard").
# The installed fdesign skill will take over and guide it step-by-step.

# 5. Preview the result
fdesign preview
# Opens http://localhost:<port>
```

---

## For Contributors

Because fdesign is fundamentally a tool focused on **Agent Engineering**, we welcome contributors looking to expand the toolkit of supported Agents or harden the validation mechanics of the CLI! 

### Getting Started

```bash
# 1. Fork and clone the repository
git clone https://github.com/lijma/fdesign.git
cd fdesign

# 2. Install inside a virtual environment for development
pip install -e ".[test]"

# 3. Run the test suite (fdesign maintains 100% coverage)
pytest tests/

# 4. Want to add a new AI Agent to `fdesign enable`?
# Add yours directly in: src/fdesign/skills.py
```

---

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=lijma/fdesign&type=Date)](https://star-history.com/#lijma/fdesign&Date)

---

## License

This project is licensed under the [Apache License 2.0](LICENSE).
