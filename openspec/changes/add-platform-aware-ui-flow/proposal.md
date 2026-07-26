## Why

The first fdesign interaction currently gathers product intent but does not establish the target platform. As a result, an agent can create a desktop-oriented prototype when the requested product is a native mobile experience, losing expected mobile navigation, modal, viewport, and interaction conventions.

Making platform selection explicit before a project exists preserves the current web workflow while ensuring mobile prototypes are designed as mobile applications from their first screen. The workflow must also leave a clear extension point for additional device classes.

## What Changes

- Add a platform-discovery gate to the first fdesign design/prototype interaction when no fdesign project exists. The agent asks the target user whether the product is Web or Mobile, while acknowledging future platform types.
- For Web, retain the existing workflow and ask whether responsive behavior is required before planning or building the prototype.
- For Mobile, retain the token → sitemap → component → build → validation workflow, but require a mobile-specific design brief and mobile UI conventions for the generated prototype.
- Separate target-platform selection from design-direction selection for Mobile: after choosing iOS, Android, both, or another device target, let the user choose a neutral brand UI, a platform-native system (iOS-native/SwiftUI or Google Material 3), or another named design system.
- Define iOS, Android, and cross-platform behavior from the selected design direction, avoiding accidental mixing of platform conventions while allowing an explicitly named custom system.
- Require mobile pages to use a phone-sized viewport/layout and mobile navigation, overlays, and page transitions appropriate to the chosen platform; keep device-frame rendering in the preview wrapper rather than embedding a phone shell in journey HTML.
- Add validation/checklist guidance so agents review responsive web behavior or mobile interaction patterns before presenting a page.

## Capabilities

### New Capabilities

- `platform-aware-prototype-workflow`: Establishes first-run platform discovery and the Web/Mobile workflow requirements for fdesign agents.

### Modified Capabilities

- None.

## Impact

- Affected agent instruction templates in `src/fdesign/skills.py` and generated integrations from `fdesign enable`.
- Potentially affected PRD/sitemap metadata and prototype guidance, validation/check tooling, preview documentation, and their tests.
- No change to the existing design-token, component, journey-map, or preview-frame architecture is intended; mobile support must remain compatible with plain responsive journey HTML.
