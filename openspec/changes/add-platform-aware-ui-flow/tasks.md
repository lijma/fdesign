## 1. Define durable platform context

- [x] 1.1 Inspect the current PRD/project metadata schema and choose the backward-compatible location for `target_platform`, `responsive_web`, `mobile_targets`, `design_direction`, and `design_system`.
- [x] 1.2 Update new-project brief/template guidance to capture the selected target and design direction without invalidating existing project files.
- [x] 1.3 Add schema or parsing tests covering absent legacy fields, Web responsive variants, neutral-brand Mobile, iOS-native, Material 3, and named custom-system variants.

## 2. Add platform-aware agent workflow

- [x] 2.1 Update the always-on fdesign instruction so a first-run design/prototype interaction checks for an existing project and asks for Web, Mobile, or another named target when none exists.
- [x] 2.2 Add the Web branch that asks for responsive behavior, records the decision, and requires viewport-based review when responsiveness is requested.
- [x] 2.3 Add the Mobile branch that asks for mobile target(s) and then neutral-brand, platform-native, or custom design direction before artifacts are built and records the resolved design system.
- [x] 2.4 Map a single-target platform-native choice to iOS-native/SwiftUI or Google Material 3; require separate variants for a multi-target platform-native choice and request a named reference for custom direction.
- [x] 2.5 Update the prototype skill's Sketch, component, build, and confirm steps with a compact Mobile checklist: phone viewport, touch-first/safe-area-aware layout, page-stack navigation, platform-appropriate branding, and consistent menus, dialogs, sheets, and dismissal paths.
- [x] 2.6 Preserve and clarify that journey HTML is plain responsive UI and that the preview wrapper, not the journey page, owns phone/tablet/desktop frames.

## 3. Document design conventions

- [x] 3.1 Add developer-facing guidance/examples for iOS-native branding and navigation: tint/semantic colors, system-first typography, SF Symbols, app-icon variants, navigation stacks, top-level tabs, sheets/action sheets, and modal dismissal.
- [x] 3.2 Add developer-facing guidance/examples for Material 3 branding and navigation: color schemes, typography, shapes, static/dynamic color behavior, back behavior, dialogs, and bottom sheets.
- [x] 3.3 Define and document the neutral-brand direction, its token derivation, and its rule against unintentional iOS/Android pattern mixing.
- [x] 3.4 Define the custom-system intake: required system name/reference and how it maps into fdesign tokens and components.
- [x] 3.5 Update README or relevant user documentation to describe Web responsive selection, Mobile target/direction selection, Mobile HTML-prototype scope, and preview device frames.

## 4. Verify integrations and regressions

- [x] 4.1 Add unit tests proving `fdesign enable` output includes the first-run platform gate, responsive-Web branch, Mobile target/direction branch, and preview-owned device-shell rule.
- [x] 4.2 Add focused tests for neutral-brand, iOS-native, Material 3, multi-target native-variant, and custom-system guidance in built-in skills and generated agent adapters.
- [x] 4.3 Run the focused project/skill/adapter tests and the full test suite; fix regressions.
- [x] 4.4 Manually exercise a new Web-responsive flow plus neutral-brand, iOS-native, Material 3, multi-target native-variant, and custom-system Mobile flows, verifying the preview wrapper supplies the device frame and each flow follows its recorded direction.
