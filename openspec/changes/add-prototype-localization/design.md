## Context

fdesign stores all generated prototype artifacts beneath `.fdesign/projects/<project>/build/` and its preview shell renders journey pages in a same-origin iframe. The repository's existing `locale/*.json` examples use the Lokalise-compatible convention of a flat JSON object: dotted string keys map to string values, including positional placeholders such as `{0}`. There is currently no localization context in the agent workflow and preview has no language control.

## Goals / Non-Goals

**Goals:**

- Discover source and supported languages before an agent creates localized prototype artifacts.
- Keep translations portable as flat, per-language JSON files compatible with the existing Lokalise-style examples.
- Let preview switch the visible language without rebuilding or duplicating journey HTML.
- Make language initialization, additions, removals, listing, and validation safe, repeatable CLI operations which the agent can invoke.
- Preserve the current behavior for projects that do not opt into localization.

**Non-Goals:**

- Connecting to Lokalise or another translation-management API.
- Machine-translation guarantees, pluralization/ICU-message compilation, right-to-left layout automation, or production application i18n runtime support.
- Translating arbitrary hardcoded page text at preview time; pages must explicitly carry translation keys.

## Decisions

### 1. Use optional flat JSON artifacts under the project build directory

Localized projects use `.fdesign/projects/<project>/build/locale/<locale>.json`. Each file is a UTF-8 JSON object with non-empty dotted-string keys and string values, matching the existing root `locale/` reference format. Locale file names use a BCP 47-compatible language identifier with `_` accepted for existing Lokalise naming conventions (for example `en.json`, `fr_FR.json`).

The agent records the source locale and requested locales in the optional PRD design context, but `build/locale/` remains the preview's source of truth. This keeps locale files portable with the build and avoids adding a proprietary catalog format.

**Alternative considered:** A nested JSON format or a custom manifest. Rejected because it diverges from the provided Lokalise examples and makes handoff harder.

### 2. Require explicit, stable keys in journey HTML

The agent writes source-language text into journey HTML and marks localizable text with `data-i18n="key"`. It marks translatable attributes with `data-i18n-attr="attribute:key"`, allowing examples such as `placeholder:login.email` and `aria-label:menu.close`. Keys are semantic and stable (for example `login.submit`), never derived from translated text.

The source-locale JSON contains every key used by journey HTML. Each additional locale contains the same key set and preserves placeholders, line breaks, and required markup semantics. This makes agent-generated language additions deterministic: it finds missing keys and translates using the PRD, sitemap, visible source copy, and component/page context.

**Alternative considered:** Have preview infer strings from text nodes. Rejected because it cannot preserve meaning, distinguish repeated strings, or safely update attributes.

### 3. Add preview-owned language selection only when locale files exist

`render_preview_index` discovers valid `build/locale/*.json` files. When at least one is available, the preview toolbar shows a language selector. It defaults to a matching browser language, then `en` if present, then the first sorted locale. The selection is retained while navigating pages in the preview.

Because preview and journey iframe share an origin, preview loads the selected catalog and applies it to the iframe DOM after it loads. It updates `[data-i18n]` text and supported `data-i18n-attr` attributes. The journey page's original source text remains the graceful fallback when opened outside preview or when a key/catalog cannot be loaded.

The agent treats this preview control as sufficient for demonstrating localization. It asks only for source and supported languages, not for a switching method. It does not add an in-product selector, language-specific pages, URL parameters, or auto-detection unless the user explicitly requests product-level language switching.

**Alternative considered:** Embed a new JavaScript runtime in every page. Rejected because a preview-owned implementation avoids a second runtime artifact and works for journey pages at any directory depth.

### 4. Manage catalog lifecycle through `fdesign locale` commands

For a new project, the agent first confirms platform and core-product requirements, then asks whether localization is needed before it runs `fdesign init`, creates a project, or creates the PRD. If localization is needed, it collects the source and supported target languages and records them in the first PRD. It then initializes the source catalog with `fdesign locale init`, and uses `fdesign locale add <locale>` for each requested target language. The CLI owns safe directory creation, locale-name validation, duplicate prevention, source-key scaffolding, removal, listing, and catalog validation. At any later iteration, a user can ask to add or remove languages: the agent invokes `add` or `remove`, then fills a newly scaffolded catalog using product/business context while preserving placeholders.

The command surface is `fdesign locale init --source <locale>`, `fdesign locale add <locale>`, `fdesign locale remove <locale>`, `fdesign locale list`, and `fdesign locale validate`. Commands resolve the current fdesign project using the same project-selection conventions as existing prototype commands. `init` creates a source catalog only when locale management is not already initialized; `add` copies the current source key inventory; `remove` never removes the final source catalog. The workflow explicitly asks for clarification rather than inventing an ambiguous locale code or industry-specific translation whose meaning cannot be inferred from available context.

**Alternative considered:** Let the agent create and delete JSON files directly. Rejected because the lifecycle would be inconsistent across agents, bypass validation, and make ordinary language maintenance dependent on manual filesystem operations.

### 5. Extend validation instead of silently accepting malformed catalogs

`fdesign locale validate` checks file-name safety, valid JSON, flat string maps, duplicate-free keys (inherent in parsed JSON), key parity with the source catalog, and placeholder parity across translations. `fdesign prototype validate` invokes the same locale validation whenever `build/locale/` exists, aggregates its errors with other prototype checks, and does not skip locale diagnostics merely because another expected artifact is absent. Preview omits invalid catalogs and reports a useful failure through existing validation rather than rendering partial/unreliable language choices.

## Risks / Trade-offs

- [Agent translation is contextually wrong] → Require it to use PRD/sitemap/page context and ask for clarification where meaning is ambiguous; keep JSON editable for user review.
- [Longer translations break layouts] → Include each requested language in the agent's page-review checklist and retain responsive/mobile checks.
- [Incomplete catalogs produce mixed language] → Validate key and placeholder parity; preview retains source text as a resilient fallback.
- [Locale file names vary] → Accept common BCP 47 and Lokalise underscore forms while displaying a readable label with a code fallback.
- [Pages opened outside preview do not switch language] → Source-language page content remains usable; live switching is intentionally a local-preview feature.
- [Agent introduces an unrequested language-setting UI] → Explicitly distinguish preview switching from product behavior in the installed skill and require an explicit user request for product-level switching.

## Migration Plan

1. Add optional localization context and instructions; for new projects, collect it before workspace/project/PRD creation. Existing PRDs and prototypes remain valid without changes.
2. Add `fdesign locale` lifecycle commands, catalog discovery, validation, and preview language switching behind the presence of `build/locale/`.
3. Update tests with CLI lifecycle behavior, flat catalogs, malformed catalogs, catalog parity, validation aggregation, and iframe/toolbar rendering cases.
4. Roll back by removing `build/locale/`; preview automatically returns to its current single-language behavior.

## Open Questions

- What is the preferred strategy for right-to-left languages once a user requests Arabic, Hebrew, or another RTL locale?
