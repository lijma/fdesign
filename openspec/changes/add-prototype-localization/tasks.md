## 1. Define locale artifacts and validation

- [x] 1.1 Add optional source-language and supported-language context to the PRD/template guidance while preserving legacy project compatibility.
- [x] 1.2 Implement locale catalog discovery under `build/locale/` with accepted locale filenames and flat Lokalise-compatible JSON parsing.
- [x] 1.3 Update `fdesign prototype validate` to aggregate locale diagnostics with other prototype checks and report malformed catalogs, invalid file names, non-string values, source/translation key drift, and placeholder mismatches.
- [x] 1.4 Add unit tests for valid catalogs, absent locale directories, malformed JSON, invalid values, key parity, and placeholder parity.

## 2. Add CLI locale lifecycle

- [x] 2.1 Add `fdesign locale init --source <locale>` to safely initialize the current project's source catalog and locale directory.
- [x] 2.2 Add `fdesign locale add`, `remove`, and `list` commands with locale-name validation, source-key scaffolding, duplicate prevention, and source-catalog protection.
- [x] 2.3 Add `fdesign locale validate` and reuse the same locale-validation implementation from `fdesign prototype validate`.
- [x] 2.4 Add CLI unit tests covering initialization, addition, removal, listing, invalid lifecycle operations, and direct validation.

## 3. Add localization-aware agent workflow

- [x] 3.1 Update always-on instructions and the fdesign skill to ask about localization, source language, and supported languages before localized artifact generation.
- [x] 3.2 Document localized journey markup using stable `data-i18n` text keys and `data-i18n-attr` attribute mappings, preserving source text as a fallback.
- [x] 3.3 Update agent workflow guidance to invoke `fdesign locale` for initialization, language additions, validation, and safe removals before translating or reviewing catalog content.
- [x] 3.4 Add localization review guidance for translated copy expansion and unresolved translation ambiguity.
- [x] 3.5 Update agent guidance so preview owns default language switching and the agent asks about product-level switching only on an explicit user request.
- [x] 3.6 Update new-project discovery guidance so localization is asked after platform and core requirements but before `fdesign init`, project creation, or PRD creation; skip it for existing projects with recorded context.

## 4. Add preview language switching

- [x] 4.1 Extend preview data loading to discover valid locale catalogs and choose an initial locale from browser preference, `en`, or sorted fallback.
- [x] 4.2 Render a language selector only when locale catalogs are available and retain its selection while navigating preview pages.
- [x] 4.3 Apply selected catalogs to keyed text and supported keyed attributes in the same-origin journey iframe after each page load, retaining source text when a key is unavailable.
- [x] 4.4 Add preview unit tests for selector visibility, default selection, switching behavior, navigation persistence, and projects without localization.

## 5. Document and verify the end-to-end flow

- [x] 5.1 Update README with CLI localization setup, `build/locale/<locale>.json` format, preview behavior, and agent-managed language changes.
- [x] 5.2 Update integration-style skill tests to verify localization discovery, CLI lifecycle guidance, and localization-markup guidance are present.
- [x] 5.3 Run focused locale/preview/skill/CLI tests and the full test suite with the project’s 100% coverage threshold; fix all failures.
- [x] 5.4 Manually exercise a localized journey with at least two catalogs and verify CLI lifecycle operations and preview switching without a device-shell regression.
- [x] 5.5 Add regression tests that assert installed agent guidance does not solicit a switching method by default.
- [x] 5.6 Add regression tests that assert localization discovery precedes workspace/project/PRD creation for new projects.
