## Context

fdesign exposes `fdesign enable <agent>` through a registry of platform adapters. Existing AGENTS.md adapters safely replace only the marker-delimited fdesign section and, where their target supports skills, also write a complete per-skill `SKILL.md`. Codex projects use project-local skills under `.codex/skills/` and can use `AGENTS.md` for always-on repository guidance.

## Goals / Non-Goals

**Goals:**

- Make `fdesign enable codex` a first-class, discoverable CLI target.
- Install a complete project-local Codex skill and always-on fdesign discovery guidance.
- Preserve non-fdesign user content in `AGENTS.md` on repeated installation.
- Cover success, refresh, preservation, and registry/help paths with the full suite at 100% coverage.

**Non-Goals:**

- Installing or modifying global Codex user configuration.
- Replacing unrelated `.codex` skills, `AGENTS.md` content, or user-owned agent configuration.
- Changing fdesign's shared workflow content or introducing a Codex-specific runtime dependency.

## Decisions

### 1. Use a Codex-specific adapter layered on the shared AGENTS.md behavior

`CodexAdapter` extends `_AgentsMdAdapter` with `_skills_subdir = "codex"`. This reuses marker-delimited `AGENTS.md` refresh behavior while producing `.codex/skills/fdesign/SKILL.md`, whose frontmatter and body use the existing common renderer.

**Alternative considered:** AGENTS.md only. Rejected because Codex's project-local skill directory provides the complete on-demand workflow without placing the entire skill body in the always-on file.

### 2. Preserve user-authored configuration outside fdesign ownership

The adapter writes only `.codex/skills/fdesign/SKILL.md` and replaces the existing `<!-- fdesign:skills -->` through `<!-- /fdesign:skills -->` section. Reinstallation is idempotent and leaves all other `AGENTS.md` content and other Codex skills unchanged.

**Alternative considered:** Replace `AGENTS.md` wholesale. Rejected because it destroys user instructions and conflicts with the behavior of existing adapters.

### 3. Validate through public CLI and filesystem contracts

Tests cover `SUPPORTED_AGENTS`, `fdesign enable codex`, generated skill frontmatter/content, the discovery section, repeated installation, marker replacement, and preservation of unrelated files. The full suite runs with `--cov-fail-under=100`.

## Risks / Trade-offs

- [Codex directory conventions evolve] → Keep the adapter isolated and test exact generated paths, making future migration localized.
- [Existing AGENTS.md content is overwritten] → Use the shared marker replacement behavior and test preservation explicitly.
- [Skill discovery is unclear] → Write both project-local skill and concise AGENTS.md discovery guidance.

## Migration Plan

1. Add the adapter and registry entry without altering existing adapter paths.
2. Document `fdesign enable codex` alongside other supported agents.
3. Verify full coverage and reinstall the local fdesign CLI after the change.
4. Roll back by removing only the Codex registry entry and adapter; generated project files remain user-removable.

## Open Questions

- None.
