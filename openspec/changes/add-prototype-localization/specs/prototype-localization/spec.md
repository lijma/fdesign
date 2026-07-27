## ADDED Requirements

### Requirement: Localization discovery before project initialization
For a new fdesign project, after platform and core-product requirements are known but before the agent runs `fdesign init`, creates a project, or creates a PRD, it SHALL ask the user whether localization is required. If it is required, the agent SHALL capture one source language and the supported language set and record them in the first project design context.

#### Scenario: Localization requested for a new prototype
- **WHEN** platform and core-product requirements have been confirmed for a new project
- **THEN** the agent SHALL ask whether localization is required before initializing the workspace/project or creating the PRD and SHALL capture the source and supported languages when it is required

#### Scenario: Localization not requested
- **WHEN** the user declines localization during new-project discovery
- **THEN** the agent SHALL continue with workspace/project/PRD creation without creating a locale directory or requiring localization markup

#### Scenario: Existing project with recorded localization context
- **WHEN** an existing project's PRD already records source and supported languages
- **THEN** the agent SHALL not ask the localization-discovery questions again unless the user asks to change the language set

### Requirement: Lokalise-compatible locale catalogs
For a localized project, the system SHALL store one UTF-8 JSON catalog per language at `.fdesign/projects/<project>/build/locale/<locale>.json`. Each catalog SHALL be a flat object whose non-empty keys and values are strings, using dotted keys compatible with the repository's `locale/` reference files.

#### Scenario: Source catalog initialized
- **WHEN** the agent initializes localization for the first time with `fdesign locale init --source <locale>`
- **THEN** the CLI SHALL create the source-language catalog and localization directory without requiring a manual filesystem operation

#### Scenario: Locale catalog validation
- **WHEN** `fdesign prototype validate` runs for a project containing `build/locale/`
- **THEN** it SHALL include locale validation and report invalid JSON, non-flat/non-string entries, invalid locale filenames, missing/extra keys, or placeholder mismatches between a translated catalog and the source catalog, even if another prototype artifact also has validation errors

### Requirement: CLI locale lifecycle
The system SHALL provide `fdesign locale init`, `add`, `remove`, `list`, and `validate` commands for the current fdesign project. The commands SHALL own creation and deletion of `build/locale` artifacts, reject invalid locale identifiers and unsafe lifecycle transitions, and use the same validation rules as `fdesign prototype validate`.

#### Scenario: Add a language through the CLI
- **WHEN** a user or agent runs `fdesign locale add <locale>` after source localization has been initialized
- **THEN** the CLI SHALL create `<locale>.json` from the complete source key inventory and SHALL reject an invalid or already-existing locale

#### Scenario: Remove a language through the CLI
- **WHEN** a user or agent runs `fdesign locale remove <locale>` for a non-source catalog
- **THEN** the CLI SHALL remove only that catalog and SHALL not modify remaining catalogs

#### Scenario: Protect the source catalog
- **WHEN** a user or agent attempts to remove the only source catalog
- **THEN** the CLI SHALL reject the operation and retain the localization artifacts

#### Scenario: List and validate catalogs through the CLI
- **WHEN** a user or agent runs `fdesign locale list` or `fdesign locale validate`
- **THEN** `list` SHALL report the available locale identifiers and `validate` SHALL report the same catalog consistency failures that prototype validation reports

### Requirement: Keyed journey content
The agent SHALL mark localizable journey text with stable `data-i18n` keys and localizable attributes with `data-i18n-attr` mappings. It SHALL keep source-language text in the HTML as the fallback and SHALL use the same keys in every locale catalog.

#### Scenario: Localizable text and attribute
- **WHEN** the agent writes a localized button label and an input placeholder
- **THEN** the HTML SHALL retain source values and expose a `data-i18n` text key and a `data-i18n-attr` placeholder key that match the source catalog

#### Scenario: Placeholder-bearing translation
- **WHEN** a source value contains a positional placeholder such as `{0}`
- **THEN** every translated value for that key SHALL contain the same placeholder set

### Requirement: Preview language selector
When a project build has one or more valid locale catalogs, fdesign preview SHALL display a language selector and apply its selected catalog to the active journey iframe. When no locale directory exists, preview SHALL not display the language selector and SHALL preserve current behavior.

#### Scenario: Switch the active preview language
- **WHEN** a user selects a valid language in preview
- **THEN** preview SHALL update keyed text and attributes in the active iframe and retain the selection while the user navigates to another journey page

#### Scenario: Default preview language
- **WHEN** preview first loads a localized project
- **THEN** it SHALL prefer a catalog matching the browser language, otherwise `en` when available, otherwise the first sorted locale

### Requirement: Preview switching is not product behavior by default
The agent SHALL use fdesign preview's language selector as the default mechanism for demonstrating localized catalogs. It SHALL ask for source and supported languages only, and SHALL NOT ask how language switching should work or add product-level switching UI unless the user explicitly requests that product behavior.

#### Scenario: Standard localization request
- **WHEN** a user asks to add internationalization support without requesting an in-product language setting
- **THEN** the agent SHALL collect source and supported languages, configure locale catalogs, and rely on preview's selector without asking a switching-method question or changing product navigation

#### Scenario: Explicit product-level language switching request
- **WHEN** a user explicitly requests an in-product language selector, language-specific routes, or automatic language detection
- **THEN** the agent SHALL clarify the requested product behavior before implementing it

### Requirement: Agent-guided language maintenance
The agent SHALL let users add or remove a supported language at any point in the prototype workflow. On addition, it SHALL invoke the locale CLI to create a complete catalog, then translate each source key using available product and business context. On removal, it SHALL invoke the locale CLI to remove only the requested locale catalog and its preview choice.

#### Scenario: Add a language
- **WHEN** the user asks to add a language to a localized prototype
- **THEN** the agent SHALL invoke the CLI to scaffold the locale catalog with source-key parity, preserve placeholders, translate values from available context, and run localization validation before presenting the update

#### Scenario: Remove a language
- **WHEN** the user asks to remove a supported language
- **THEN** the agent SHALL invoke the CLI to remove that locale catalog without changing source keys or the remaining language catalogs
