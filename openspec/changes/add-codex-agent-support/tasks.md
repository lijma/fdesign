## 1. Add the Codex adapter

- [x] 1.1 Implement `CodexAdapter` using the shared AGENTS.md marker-refresh behavior and `.codex/skills/` as its skill directory.
- [x] 1.2 Register `codex` in the adapter registry and `SUPPORTED_AGENTS` so `fdesign enable codex` is accepted and shown in help.

## 2. Document Codex support

- [x] 2.1 Add Codex to the README supported-agent table and describe its enable command.
- [x] 2.2 Verify generated `AGENTS.md` points users to `.codex/skills/fdesign/SKILL.md` without duplicating the full workflow body.

## 3. Verify behavior and coverage

- [x] 3.1 Add adapter tests for fresh installation, generated skill frontmatter/content, registry visibility, and CLI enable output.
- [x] 3.2 Add tests for idempotent refresh, stale-marker replacement, and preservation of unrelated AGENTS.md content and Codex skills.
- [x] 3.3 Run the complete test suite with `--cov=src/fdesign --cov-fail-under=100`; fix all failures until statement coverage is 100%.
- [x] 3.4 Reinstall the local fdesign CLI, rehash pyenv, and verify `fdesign --version` after implementation.
