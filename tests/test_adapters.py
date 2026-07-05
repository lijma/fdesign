"""Tests for fdesign adapters."""

from fdesign.adapters import (
    ADAPTERS,
    SUPPORTED_AGENTS,
    ClaudeAdapter,
    CopilotAdapter,
    CursorAdapter,
    OpenClawAdapter,
    OpenCodeAdapter,
    QwenCodeAdapter,
    TraeAdapter,
)
from fdesign.skills import INSTRUCTION, SKILLS


def test_supported_agents_registered():
    assert set(ADAPTERS) == set(SUPPORTED_AGENTS)


def test_skill_registry_is_prototype_only():
    assert list(SKILLS) == ["prototype"]
    assert SKILLS["prototype"]["name"] == "fdesign-prototype"
    assert "fdesign journey check" in INSTRUCTION


def test_copilot_adapter(tmp_path):
    created = CopilotAdapter().install(tmp_path)
    assert (tmp_path / ".github" / "instructions" / "fdesign.instructions.md").exists()
    assert (tmp_path / ".github" / "skills" / "fdesign-prototype" / "SKILL.md").exists()
    assert len([path for path in created if path.name == "SKILL.md"]) == 1


def test_cursor_adapter(tmp_path):
    created = CursorAdapter().install(tmp_path)
    assert (tmp_path / ".cursor" / "rules" / "fdesign.mdc").exists()
    assert any(path.name == "fdesign-prototype.mdc" for path in created)


def test_claude_adapter_variants(tmp_path):
    adapter = ClaudeAdapter()
    adapter.install(tmp_path)
    adapter.install(tmp_path)
    content = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert content.count("fdesign:skills") == 2

    claude = tmp_path / "CLAUDE.md"
    claude.write_text("# Existing\n", encoding="utf-8")
    adapter.install(tmp_path)
    assert "# Existing" in claude.read_text(encoding="utf-8")

    claude.write_text("# Existing\n<!-- fdesign:skills -->\nold", encoding="utf-8")
    adapter.install(tmp_path)
    content = claude.read_text(encoding="utf-8")
    assert "old" not in content
    assert "fdesign-prototype" in content


def test_trae_adapter(tmp_path):
    created = TraeAdapter().install(tmp_path)
    assert created == [tmp_path / ".trae" / "project_rules.md"]
    assert "fdesign-prototype" in created[0].read_text(encoding="utf-8")


def test_agents_md_adapters(tmp_path):
    assert QwenCodeAdapter().install(tmp_path) == [tmp_path / "AGENTS.md"]
    OpenCodeAdapter().install(tmp_path)
    assert (tmp_path / ".opencode" / "skills" / "fdesign-prototype" / "SKILL.md").exists()
    OpenClawAdapter().install(tmp_path)
    assert (tmp_path / ".openclaw" / "skills" / "fdesign-prototype" / "SKILL.md").exists()

    agents = tmp_path / "AGENTS.md"
    agents.write_text("# Existing\n", encoding="utf-8")
    OpenCodeAdapter().install(tmp_path)
    assert "# Existing" in agents.read_text(encoding="utf-8")

    agents.write_text("# Existing\n<!-- fdesign:skills -->\nold", encoding="utf-8")
    OpenCodeAdapter().install(tmp_path)
    content = agents.read_text(encoding="utf-8")
    assert "old" not in content
    assert "fdesign-prototype" in content
