## Why

fdesign can install its workflow for several coding agents, but Codex users cannot currently enable the same guided prototype workflow with `fdesign enable codex`. Supporting Codex lets its project-local skill system discover fdesign's platform-aware and localization-aware instructions consistently.

## What Changes

- Add `codex` as a supported target for `fdesign enable`.
- Install the complete fdesign skill at `.codex/skills/fdesign/SKILL.md`, using the Codex-compatible skill frontmatter and Markdown body.
- Add or refresh a marker-delimited fdesign discovery section in the project `AGENTS.md`, preserving user-authored content outside that section.
- Document Codex support in the CLI help and README supported-agent table.
- Add unit and integration-style adapter tests, retaining the repository's 100% coverage requirement.

## Capabilities

### New Capabilities

- `codex-agent-adapter`: Defines installation, discovery, idempotent refresh, and documentation behavior for Codex projects.

### Modified Capabilities

- None.

## Impact

- Affects `src/fdesign/adapters.py`, CLI agent choices/help, README, and adapter tests.
- Creates or updates only project-local `.codex/skills/fdesign/SKILL.md` and the fdesign-owned marker section of `AGENTS.md` when users run `fdesign enable codex`.
- Adds no runtime dependency.
