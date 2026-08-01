## ADDED Requirements

### Requirement: Codex is an enable target
The system SHALL list `codex` as a supported agent and SHALL accept `fdesign enable codex` using the same project-directory option as other adapters.

#### Scenario: Discover Codex support
- **WHEN** a user runs `fdesign enable --help`
- **THEN** the output SHALL list `codex` as a supported agent

#### Scenario: Enable Codex in a project
- **WHEN** a user runs `fdesign enable codex --project-dir <project>`
- **THEN** the command SHALL complete successfully and report the created Codex configuration paths

### Requirement: Codex skill installation
The system SHALL install the complete fdesign skill at `.codex/skills/fdesign/SKILL.md` with valid skill frontmatter and the shared fdesign workflow body.

#### Scenario: Fresh Codex installation
- **WHEN** Codex support is enabled in a project without a fdesign Codex skill
- **THEN** the system SHALL create `.codex/skills/fdesign/SKILL.md` containing the fdesign skill name, description, and workflow content

#### Scenario: Preserve unrelated Codex skills
- **WHEN** Codex support is enabled in a project containing another `.codex/skills/` entry
- **THEN** the system SHALL not modify or remove that unrelated skill

### Requirement: Safe Codex discovery refresh
The system SHALL create or refresh a marker-delimited fdesign section in `AGENTS.md` that points to the Codex skill. It SHALL preserve all content outside that section on repeated installation.

#### Scenario: Refresh a stale fdesign section
- **WHEN** `AGENTS.md` contains an existing fdesign marker section
- **THEN** enabling Codex SHALL replace that section with current guidance and remove stale fdesign content

#### Scenario: Preserve user instructions
- **WHEN** `AGENTS.md` contains user-authored content outside the fdesign marker section
- **THEN** enabling Codex SHALL retain that content unchanged

### Requirement: Complete coverage verification
The implementation SHALL include tests for all Codex adapter and CLI branches and SHALL pass the project's full test suite at 100% statement coverage.

#### Scenario: Run full verification
- **WHEN** the Codex support implementation is complete
- **THEN** the full test suite SHALL pass with `--cov-fail-under=100`
