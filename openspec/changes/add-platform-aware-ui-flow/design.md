## Context

fdesign has one iterative prototype workflow and its preview already wraps journey HTML in desktop, tablet, or phone device frames. The current agent instruction starts its first Sketch step by asking about product, users, and core flow, but it does not determine the platform before an agent chooses layout or navigation. The same instructions correctly require journey HTML to remain a plain responsive document and prohibit embedding a device shell.

This change adds platform context to the agent's first-run conversation and makes it drive the existing workflow. It does not create native iOS/Android applications; fdesign continues to generate HTML prototypes. The design is informed by Apple's Human Interface Guidelines for tab bars, sheets, modality, and search, and Material Design guidance for Android navigation and modal components.

## Goals / Non-Goals

**Goals:**

- Capture a primary target platform before a new fdesign project begins design work.
- Preserve the present Web workflow, with an explicit responsive-Web decision.
- Make Mobile HTML prototypes look and behave like phone app screens through platform-aware layout, navigation, modal, safe-area, and viewport guidance.
- Capture both mobile target platforms and the intended visual/interaction direction: neutral brand UI, platform-native UI, or a named custom system.
- Support iOS, Android, and a neutral cross-platform baseline without mixing conventions accidentally.
- Keep the workflow extensible to future device categories and compatible with preview-owned device frames.

**Non-Goals:**

- Building native iOS or Android binaries, adding a native UI toolkit, or asserting platform-store compliance.
- Replacing fdesign's tokens, components, sitemap, journey map, or validation architecture.
- Embedding phone/chrome mockups inside generated journey HTML.
- Defining a new detailed design system or mandating pixel-identical Apple/Material components.

## Decisions

### 1. Gate only a first-run design/prototype interaction on project existence

The agent SHALL first check whether the workspace has a fdesign project. If none exists, it asks the user for the primary target: Web, Mobile, or an explicitly named future device type. Once a project exists, normal iterative work continues from its recorded context, asking only when the platform is absent or the user changes it.

This avoids repeatedly interrupting established work. It is also narrower and safer than asking on every workflow iteration.

**Alternative considered:** Always ask for a platform. Rejected because it adds friction and risks contradicting prior project decisions.

### 2. Persist target and design-direction decisions in the project brief, with a backward-compatible fallback

The agent records `target_platform` in the PRD/project brief, together with `responsive_web` for Web. For Mobile, it records `mobile_targets` (one or more of `ios`, `android`, or a named device target), `design_direction` (`neutral-brand`, `platform-native`, or `custom`), and the resolved `design_system` (`ios-native`, `material3`, `neutral-brand`, or a user-supplied identifier). Existing projects without these fields remain valid; the agent asks for the missing context when it next performs design work.

The guided conversation intentionally separates these questions:

1. Which mobile target or targets matter?
2. Should the prototype use a neutral branded UI, adhere to the target platform, or use another named design system?

For a single iOS target, `platform-native` resolves to `ios-native`/SwiftUI and Apple HIG conventions. For a single Android target, it resolves to Google Material 3. For multiple targets, a neutral-brand system is the default recommendation; a platform-native choice requires separately identified iOS and Android variants rather than a blended single screen. A `custom` direction requires the user to name the desired system or provide a reference.

This keeps platform intent available across sessions without requiring a project-index migration. The exact durable field location will be selected during implementation after verifying the PRD schema and agent-facing template.

**Alternative considered:** Add platform columns to the global project index immediately. Rejected because that index is project-discovery metadata, while platform is product-design context, and it would need a migration path.

### 3. Branch the current workflow by target and design direction, rather than create a mobile-only workflow

Both paths use Token → Sitemap → Component → Build → Validate → Check → Confirm. The Web branch asks whether responsive behavior is required. If it is, the agent specifies the supported widths and verifies layouts at appropriate preview sizes; otherwise, it documents the fixed/primary Web target.

The Mobile branch asks for mobile targets first and then for the design direction before it writes the PRD, sitemap, component definitions, or page. It treats every journey page as a phone screen, includes the mobile viewport meta tag, respects safe areas where fixed controls meet screen edges, and uses touch-first target sizing, hierarchy, and scroll behavior. The chosen direction drives token/component selection: neutral-brand maps product branding tokens to a platform-neutral component set; iOS-native maps them to Apple-native color, type, icon, and interaction conventions; Material 3 maps them to Material color roles, typography, shape, and components.

**Alternative considered:** Require a separate mobile command and artifact tree. Rejected because it duplicates fdesign's quality loop and makes shared design tokens/components harder to reuse.

### 4. Express mobile conventions as component and flow choices, not a device-shell DOM wrapper

For iOS-native, the generated design follows an iOS navigation stack for hierarchical screens, a tab bar only for top-level sections, and sheets/action sheets or full-screen presentation for focused tasks. It provides a clear dismissal path and does not stack modal experiences unnecessarily. Brand expression uses Apple-compatible mechanisms such as accent/tint color, semantic/dynamic colors, typography within the system-first hierarchy, SF Symbols, and app-icon variants.

For Material 3, the generated design uses Material-oriented top-level navigation (for example, bottom navigation for a small set of primary destinations), predictable back navigation, and dialogs or bottom sheets for focused choices. Its product branding maps to M3 color schemes, typography, and shapes, with optional Android dynamic color and a static branded fallback. For neutral-brand products, the agent uses brand-derived tokens and one coherent neutral interaction pattern per flow. It MUST NOT combine recognizably iOS and Android navigation/modal patterns on the same screen without an explicit product reason. A custom design system is used only when the user names it or provides a sufficient reference.

The journey HTML remains ordinary responsive page content; fdesign preview remains the sole owner of phone/tablet/desktop shells. A mobile prototype is made convincing through its viewport, layout, components, and interactions—not by drawing a phone inside an iframe.

**Alternative considered:** Require an image-like phone mockup in each HTML page. Rejected because it conflicts with the preview architecture, harms reuse at other viewport sizes, and produces non-production UI.

### 5. Make the guidance testable through explicit pre-build and review checklists

The installed agent skills will include a compact platform checklist before building and before presenting work. Tests assert that generated agent integrations contain the discovery gate, Web responsive prompt, mobile platform branch, no-device-shell rule, and the relevant mobile conventions.

**Alternative considered:** Add a heuristic CLI validator that infers platform correctness from HTML. Rejected for this change because native-pattern correctness is contextual and heuristic enforcement would create brittle false failures; the existing structural validators remain unchanged.

## Risks / Trade-offs

- [Platform conventions evolve] → Keep the instructions principle-oriented and cite Apple HIG/Material sources in developer documentation; update examples independently of the core flow.
- [Mobile and Web requests are ambiguous] → Ask the platform question only before initialization and ask a focused follow-up for responsive Web or mobile platform selection.
- [Cross-platform output becomes visually inconsistent] → Require an explicit neutral-brand, platform-native, or custom direction and prohibit unintentional mixing.
- [A multi-target native request produces a hybrid screen] → Require separate identified platform variants for iOS-native and Material 3 output; recommend neutral-brand UI for a single shared prototype.
- [Mobile support is mistaken for native-app generation] → State clearly in instructions and documentation that the deliverable remains an HTML prototype.
- [Existing projects lack platform metadata] → Treat missing fields as an on-demand clarification rather than failing or migrating projects.

## Migration Plan

1. Update the built-in instruction and prototype skill templates with the target-then-direction conversation, then regenerate/install integrations through the existing `fdesign enable` flow.
2. Add optional platform context to new project briefs; leave existing briefs untouched until the next relevant interaction.
3. Add focused unit tests for template content and any chosen PRD schema handling, then run the existing test suite.
4. Roll back by removing the new optional guidance and metadata handling; existing project files and generated journey pages remain valid.

## Open Questions

- Should implementation add an explicit `fdesign project set-platform`/`set-design-system` CLI command, or is agent-managed PRD context sufficient for the first release?
- Which responsive-Web viewport matrix should be the documented default when the user wants responsiveness but supplies no device requirements?
