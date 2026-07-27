## Why

fdesign prototypes currently hardcode visible copy into journey HTML, so an agent cannot reliably create, review, or demonstrate a product in more than one language. Internationalization needs to become part of the prototype workflow before page generation, while preserving a portable translation format that localization tools can consume.

## What Changes

- Add a localization discovery step to the fdesign agent skill after platform and core-product discovery but before it initializes an fdesign workspace/project or creates a PRD; the agent asks whether localization is needed and, if so, identifies the source and supported languages.
- Store prototype translations in `.fdesign/projects/<project>/build/locale/<locale>.json` using flat, dotted-key Lokalise-compatible JSON files like the repository's `locale/` examples.
- Require localized journey HTML to use stable translation keys, enabling the agent to maintain matching keys across languages and translate added languages from product/business context.
- When a build contains a `locale/` directory with language JSON files, add a language selector to fdesign preview and apply the selected translations to the rendered journey iframe.
- Treat preview-owned language selection as the default demonstration mechanism; do not ask about or generate a product-level language switcher unless the user explicitly requests one.
- Add `fdesign locale` lifecycle commands to initialize, add, remove, list, and validate catalogs; the agent invokes these commands instead of creating or deleting `build/locale` artifacts directly.
- Enable agent-guided addition and deletion of languages at any iteration; adding a language scaffolds a complete translation file through the CLI before the agent translates it, while deletion uses the CLI to remove only the selected language artifact and its preview option.

## Capabilities

### New Capabilities

- `prototype-localization`: Defines language discovery, Lokalise-compatible locale artifacts, agent-maintained translations, and preview language switching.

### Modified Capabilities

- None.

## Impact

- Affected CLI commands, built-in fdesign skill instructions, PRD context guidance, generated journey markup conventions, preview rendering/iframe behavior, and tests.
- Introduces optional `build/locale/*.json` prototype artifacts; projects without them retain current preview behavior.
- No external localization service or runtime dependency is required.
