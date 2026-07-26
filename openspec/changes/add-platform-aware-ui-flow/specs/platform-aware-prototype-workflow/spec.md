## ADDED Requirements

### Requirement: First-run platform discovery
When a design or prototype interaction starts in a workspace with no fdesign project, the installed fdesign agent workflow SHALL ask the target user to identify the primary target platform before creating design artifacts or journey HTML. The prompt SHALL support Web and Mobile and allow the user to name another device category for future extensibility.

#### Scenario: New Web project
- **WHEN** no fdesign project exists and the user identifies Web as the target platform
- **THEN** the agent SHALL record Web as the primary target and continue through the Web branch of the workflow

#### Scenario: New Mobile project
- **WHEN** no fdesign project exists and the user identifies Mobile as the target platform
- **THEN** the agent SHALL ask for the applicable mobile target or targets and a design direction before generating prototype artifacts

#### Scenario: Existing project
- **WHEN** one or more fdesign projects already exist
- **THEN** the agent SHALL NOT repeat the first-run platform question unless the saved platform context is absent or the user requests a platform change

### Requirement: Responsive Web discovery and review
For a Web target, the agent SHALL ask whether the product requires responsive Web behavior before it plans or builds a page. The agent SHALL capture the user's answer in the project design context and use it to drive the layout review.

#### Scenario: Responsive Web requested
- **WHEN** the user states that a Web project must be responsive
- **THEN** the agent SHALL define the relevant viewport/width expectations and verify that the generated page adapts at those sizes before presenting it

#### Scenario: Fixed-width Web requested
- **WHEN** the user states that responsive behavior is not required
- **THEN** the agent SHALL document the primary Web target and SHALL NOT represent the page as responsive without a later user decision

### Requirement: Mobile target and design-direction selection
For a Mobile target, the agent SHALL preserve fdesign's existing token, sitemap, component, build, validation, and journey-check workflow while producing each journey page as a phone-oriented application screen. Before artifact generation, the agent SHALL record the applicable `mobile_targets` and ask the user to choose `neutral-brand`, `platform-native`, or `custom` design direction. The agent SHALL record the resolved `design_system` in the project design context.

#### Scenario: iOS-native direction
- **WHEN** the user selects iOS as the sole mobile target and selects platform-native direction
- **THEN** the agent SHALL record `ios-native` as the design system and use an iOS-consistent hierarchy/navigation stack, top-level tab navigation, and appropriate sheets, action sheets, or full-screen presentation

#### Scenario: Android Material 3 direction
- **WHEN** the user selects Android as the sole mobile target and selects platform-native direction
- **THEN** the agent SHALL record `material3` as the design system and use coherent Material 3 navigation and back behavior and appropriate dialogs or bottom sheets for focused choices

#### Scenario: Neutral-brand direction
- **WHEN** the user selects neutral-brand direction for one or more mobile targets
- **THEN** the agent SHALL derive the prototype from the product branding tokens, record one coherent neutral convention per flow, and SHALL NOT mix iOS- and Android-specific navigation or modal patterns without an explicit rationale

#### Scenario: Multi-target native direction
- **WHEN** the user selects both iOS and Android and selects platform-native direction
- **THEN** the agent SHALL ask whether to create separately identified `ios-native` and `material3` variants and SHALL NOT create a blended single-platform screen

#### Scenario: Custom direction
- **WHEN** the user selects custom direction
- **THEN** the agent SHALL ask the user to name the design system or provide a reference before it generates prototype artifacts

### Requirement: Mobile viewport, overlays, and page flow
Mobile journey pages SHALL be authored for a phone viewport, include mobile viewport configuration, and use touch-first layout, scrolling, and safe-area-aware placement for controls fixed to screen edges. The agent SHALL model hierarchical navigation as a page stack and SHALL provide a clear dismissal or back path for every overlay or focused task.

#### Scenario: Mobile landing page
- **WHEN** the agent creates a mobile landing page
- **THEN** the page SHALL present as a phone-screen layout with mobile-appropriate navigation and controls rather than a scaled desktop landing page

#### Scenario: Focused mobile task
- **WHEN** the agent adds a popup, menu, confirmation, or other focused task to a mobile flow
- **THEN** it SHALL use the selected baseline's dialog, sheet, action-sheet, or menu convention and SHALL expose an unambiguous dismiss, cancel, or back path

### Requirement: Preview-owned device shell
Mobile journey HTML SHALL remain a plain responsive document and SHALL NOT embed a simulated phone, tablet, or desktop shell. The fdesign preview wrapper SHALL remain responsible for rendering device frames.

#### Scenario: Mobile page preview
- **WHEN** the agent previews a mobile journey page
- **THEN** the page SHALL be rendered in the preview's phone device frame while the HTML contains only production-facing page UI

### Requirement: Platform guidance verification
The installed fdesign agent skill SHALL present target-specific and design-direction-specific pre-build and pre-delivery guidance. Automated tests SHALL verify the presence of the first-run discovery, responsive-Web, Mobile target/direction selection, and preview-owned device-shell instructions.

#### Scenario: Agent skill installation
- **WHEN** `fdesign enable <agent>` installs fdesign guidance
- **THEN** the installed instruction set SHALL contain the platform-discovery workflow, target-then-direction selection, and the applicable build/review checklist

#### Scenario: Automated regression test
- **WHEN** the fdesign test suite runs after platform-aware workflow changes
- **THEN** it SHALL detect removal of the required platform branch or the device-shell ownership rule
