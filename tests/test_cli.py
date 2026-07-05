"""Tests for fdesign CLI commands."""

import json
import shutil
import threading
import time
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from fdesign import __version__
from fdesign.cli import main
from fdesign.project import create_project, init_workspace


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def project(tmp_path):
    """A tmp workspace with .fdesign/ initialized and a 'main' project created."""
    init_workspace(tmp_path)
    create_project(tmp_path, "main")
    return tmp_path


# ---------------------------------------------------------------------------
# fdesign --version / --help
# ---------------------------------------------------------------------------


class TestMainGroup:
    def test_version(self, runner):
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert __version__ in result.output

    def test_help(self, runner):
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "fdesign" in result.output
        assert "init" in result.output
        assert "enable" in result.output
        assert "token" in result.output


# ---------------------------------------------------------------------------
# fdesign init
# ---------------------------------------------------------------------------


class TestInitCommand:
    def test_init_creates_floop_dir(self, runner, tmp_path):
        result = runner.invoke(main, ["init", "--project-dir", str(tmp_path)])
        assert result.exit_code == 0
        assert "✓" in result.output
        assert (tmp_path / ".fdesign").is_dir()
        assert (tmp_path / ".fdesign" / "config.json").exists()
        assert (tmp_path / ".fdesign" / "projects").is_dir()
        # No default project — projects are created on demand
        assert not (tmp_path / ".fdesign" / "projects" / "main").exists()

    def test_init_skips_if_exists(self, runner, project):
        result = runner.invoke(main, ["init", "--project-dir", str(project)])
        assert result.exit_code == 0
        assert "already exists" in result.output

    def test_init_writes_gitignore(self, runner, tmp_path):
        runner.invoke(main, ["init", "--project-dir", str(tmp_path)])
        gitignore = tmp_path / ".fdesign" / ".gitignore"
        assert gitignore.exists()
        content = gitignore.read_text(encoding="utf-8")
        assert "build/" in content

    def test_init_config_has_version(self, runner, tmp_path):
        runner.invoke(main, ["init", "--project-dir", str(tmp_path)])
        config = json.loads(
            (tmp_path / ".fdesign" / "config.json").read_text(encoding="utf-8")
        )
        assert "version" in config


# ---------------------------------------------------------------------------
# fdesign enable
# ---------------------------------------------------------------------------


class TestEnableCommand:
    def test_enable_copilot(self, runner, tmp_path):
        result = runner.invoke(
            main, ["enable", "copilot", "--project-dir", str(tmp_path)]
        )
        assert result.exit_code == 0
        assert "✓" in result.output
        skills_dir = tmp_path / ".github" / "skills"
        assert skills_dir.is_dir()
        # Should have at least 1 skill
        skill_dirs = list(skills_dir.iterdir())
        assert len(skill_dirs) >= 1

    def test_enable_cursor(self, runner, tmp_path):
        result = runner.invoke(
            main, ["enable", "cursor", "--project-dir", str(tmp_path)]
        )
        assert result.exit_code == 0
        rules_dir = tmp_path / ".cursor" / "rules"
        assert rules_dir.is_dir()
        mdc_files = list(rules_dir.glob("*.mdc"))
        assert len(mdc_files) >= 1

    def test_enable_claude(self, runner, tmp_path):
        result = runner.invoke(
            main, ["enable", "claude", "--project-dir", str(tmp_path)]
        )
        assert result.exit_code == 0
        skills_dir = tmp_path / ".claude" / "skills"
        assert skills_dir.is_dir()
        assert (tmp_path / "CLAUDE.md").exists()

    def test_enable_invalid_agent(self, runner, tmp_path):
        result = runner.invoke(
            main, ["enable", "invalid", "--project-dir", str(tmp_path)]
        )
        assert result.exit_code != 0


# ---------------------------------------------------------------------------
# fdesign project
# ---------------------------------------------------------------------------


class TestProjectCommand:
    def test_project_list_requires_workspace(self, runner, tmp_path):
        result = runner.invoke(main, ["project", "list", "--project-dir", str(tmp_path)])
        assert result.exit_code != 0
        assert "fdesign init" in result.output

    def test_project_list_outputs_text_and_json(self, runner, project):
        result = runner.invoke(main, ["project", "list", "--project-dir", str(project)])
        assert result.exit_code == 0
        assert "main" in result.output

        json_result = runner.invoke(
            main,
            ["project", "list", "--json-output", "--project-dir", str(project)],
        )
        assert json_result.exit_code == 0
        data = json.loads(json_result.output)
        assert data["projects"][0]["name"] == "main"

    def test_project_list_handles_empty_workspace(self, runner, tmp_path):
        (tmp_path / ".fdesign" / "projects").mkdir(parents=True)
        (tmp_path / ".fdesign" / "projects.csv").write_text(
            "name,title,created_at\n",
            encoding="utf-8",
        )
        result = runner.invoke(main, ["project", "list", "--project-dir", str(tmp_path)])
        assert result.exit_code == 0
        assert "No projects found" in result.output

    def test_project_create_and_info(self, runner, project):
        result = runner.invoke(
            main,
            [
                "project",
                "create",
                "Sales Portal",
                "--title",
                "Sales Portal",
                "--project-dir",
                str(project),
            ],
        )
        assert result.exit_code == 0
        assert "sales-portal" in result.output

        info = runner.invoke(
            main,
            ["project", "info", "--project", "sales-portal", "--project-dir", str(project)],
        )
        assert info.exit_code == 0
        assert "content:" in info.output

    def test_project_create_reports_duplicate(self, runner, project):
        result = runner.invoke(
            main,
            ["project", "create", "main", "--project-dir", str(project)],
        )
        assert result.exit_code != 0
        assert "already exists" in result.output

    def test_project_info_reports_missing(self, runner, project):
        result = runner.invoke(
            main,
            ["project", "info", "--project", "missing", "--project-dir", str(project)],
        )
        assert result.exit_code != 0
        assert "not found" in result.output


# ---------------------------------------------------------------------------
# fdesign token init
# ---------------------------------------------------------------------------


class TestTokenInitCommand:
    def test_token_init_creates_files(self, runner, project):
        result = runner.invoke(
            main, ["token", "init", "--project-dir", str(project)]
        )
        assert result.exit_code == 0
        assert "✓" in result.output
        tokens_dir = project / ".fdesign" / "projects" / "main" / "tokens"
        assert (tokens_dir / "global.tokens.json").exists()
        assert (tokens_dir / "semantic.tokens.json").exists()
        assert (tokens_dir / "component.tokens.json").exists()

    def test_token_init_without_floop_dir(self, runner, tmp_path):
        result = runner.invoke(
            main, ["token", "init", "--project-dir", str(tmp_path)]
        )
        assert result.exit_code != 0
        assert "fdesign init" in result.output

    def test_token_init_skips_if_exists(self, runner, project):
        # First init
        runner.invoke(main, ["token", "init", "--project-dir", str(project)])
        # Second init without --force
        result = runner.invoke(
            main, ["token", "init", "--project-dir", str(project)]
        )
        assert result.exit_code == 0
        assert "already exist" in result.output

    def test_token_init_force_overwrites(self, runner, project):
        runner.invoke(main, ["token", "init", "--project-dir", str(project)])
        # Modify a file
        f = project / ".fdesign" / "projects" / "main" / "tokens" / "global.tokens.json"
        f.write_text('{"modified": true}', encoding="utf-8")
        # Force overwrite
        result = runner.invoke(
            main, ["token", "init", "--force", "--project-dir", str(project)]
        )
        assert result.exit_code == 0
        assert "✓" in result.output
        data = json.loads(f.read_text(encoding="utf-8"))
        assert "modified" not in data


# ---------------------------------------------------------------------------
# fdesign token validate
# ---------------------------------------------------------------------------


class TestTokenValidateCommand:
    def test_validate_valid_tokens(self, runner, project):
        # Init tokens then validate
        runner.invoke(main, ["token", "init", "--project-dir", str(project)])
        result = runner.invoke(
            main, ["token", "validate", "--project-dir", str(project)]
        )
        assert result.exit_code == 0
        assert "✓" in result.output or "valid" in result.output.lower()

    def test_validate_json_output(self, runner, project):
        runner.invoke(main, ["token", "init", "--project-dir", str(project)])
        result = runner.invoke(
            main,
            ["token", "validate", "--json-output", "--project-dir", str(project)],
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "valid" in data
        assert "errors" in data
        assert "warnings" in data
        assert "stats" in data
        assert data["valid"] is True

    def test_validate_no_tokens(self, runner, project):
        result = runner.invoke(
            main, ["token", "validate", "--project-dir", str(project)]
        )
        assert result.exit_code == 1  # errors → exit 1
        assert "NO_TOKEN_FILES" in result.output

    def test_validate_shows_errors(self, runner, project):
        tokens_dir = project / ".fdesign" / "projects" / "main" / "tokens"
        bad = {"x": {"$type": "badType", "$value": "y"}}
        (tokens_dir / "bad.tokens.json").write_text(
            json.dumps(bad), encoding="utf-8"
        )
        result = runner.invoke(
            main, ["token", "validate", "--project-dir", str(project)]
        )
        assert result.exit_code == 1  # errors → exit 1
        assert "INVALID_TYPE" in result.output

    def test_validate_shows_warnings(self, runner, project):
        tokens_dir = project / ".fdesign" / "projects" / "main" / "tokens"
        minimal = {"custom": {"$type": "color", "$value": "#000"}}
        (tokens_dir / "min.tokens.json").write_text(
            json.dumps(minimal), encoding="utf-8"
        )
        result = runner.invoke(
            main, ["token", "validate", "--project-dir", str(project)]
        )
        assert "MISSING_RECOMMENDED" in result.output

    def test_validate_json_output_with_errors(self, runner, project):
        tokens_dir = project / ".fdesign" / "projects" / "main" / "tokens"
        (tokens_dir / "broken.tokens.json").write_text("{bad json", encoding="utf-8")
        result = runner.invoke(
            main,
            ["token", "validate", "--json-output", "--project-dir", str(project)],
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["valid"] is False
        assert len(data["errors"]) > 0


# ---------------------------------------------------------------------------
# fdesign token (group help)
# ---------------------------------------------------------------------------


class TestTokenGroup:
    def test_token_help(self, runner):
        result = runner.invoke(main, ["token", "--help"])
        assert result.exit_code == 0
        assert "init" in result.output
        assert "validate" in result.output
        assert "view" in result.output
        assert "DTCG" in result.output


# ---------------------------------------------------------------------------
# fdesign token view
# ---------------------------------------------------------------------------


class TestTokenViewCommand:
    def test_view_generates_html(self, runner, project):
        runner.invoke(main, ["token", "init", "--project-dir", str(project)])
        result = runner.invoke(
            main, ["token", "view", "--project-dir", str(project)]
        )
        assert result.exit_code == 0
        assert "✓" in result.output
        assert (project / ".fdesign" / "projects" / "main" / "build" / "tokens" / "design-tokens.html").exists()

    def test_view_without_floop_dir(self, runner, tmp_path):
        # Remove .fdesign so tokens dir doesn't exist
        result = runner.invoke(
            main, ["token", "view", "--project-dir", str(tmp_path)]
        )
        assert result.exit_code != 0

    def test_view_no_token_files(self, runner, project):
        # .fdesign/tokens/ exists but is empty
        result = runner.invoke(
            main, ["token", "view", "--project-dir", str(project)]
        )
        assert result.exit_code != 0

    def test_view_missing_tokens_dir(self, runner, project):
        tokens_dir = project / ".fdesign" / "projects" / "main" / "tokens"
        tokens_dir.rmdir()
        result = runner.invoke(
            main, ["token", "view", "--project-dir", str(project)]
        )
        assert result.exit_code != 0
        assert "tokens" in result.output

    def test_view_output_path(self, runner, project):
        runner.invoke(main, ["token", "init", "--project-dir", str(project)])
        result = runner.invoke(
            main, ["token", "view", "--project-dir", str(project)]
        )
        assert "design-tokens.html" in result.output


# ---------------------------------------------------------------------------
# fdesign preview
# ---------------------------------------------------------------------------


class TestPreviewCommand:
    def test_preview_without_floop_dir(self, runner, tmp_path):
        result = runner.invoke(
            main, ["preview", "--project-dir", str(tmp_path)]
        )
        assert result.exit_code != 0

    def test_preview_help(self, runner):
        result = runner.invoke(main, ["preview", "--help"])
        assert result.exit_code == 0
        assert "preview" in result.output.lower()
        assert "port" in result.output.lower()

    def test_preview_starts_server(self, runner, project):
        """Test that preview starts a server, showing the correct URL."""
        with patch("http.server.HTTPServer") as mock_server_cls:
            mock_server = mock_server_cls.return_value
            mock_server.serve_forever.side_effect = KeyboardInterrupt

            result = runner.invoke(
                main, ["preview", "--project-dir", str(project)]
            )
            assert result.exit_code == 0
            assert "fdesign preview server" in result.output
            assert "127.0.0.1" in result.output
            mock_server.serve_forever.assert_called_once()
            mock_server.server_close.assert_called_once()

    def test_preview_shows_token_link(self, runner, project):
        """preview starts without writing index.html into build/."""
        with patch("http.server.HTTPServer") as mock_server_cls:
            mock_server = mock_server_cls.return_value
            mock_server.serve_forever.side_effect = KeyboardInterrupt

            runner.invoke(main, ["preview", "--project-dir", str(project)])
            assert not (project / ".fdesign" / "projects" / "main" / "build" / "index.html").exists()

    def test_preview_uses_runtime_handler(self, runner, project):
        """preview passes a virtual index handler to HTTPServer."""
        build_dir = project / ".fdesign" / "projects" / "main" / "build"
        (build_dir / "design-tokens.html").write_text("<html></html>", encoding="utf-8")
        (build_dir / "home.html").write_text("<html></html>", encoding="utf-8")

        with patch("http.server.HTTPServer") as mock_server_cls:
            mock_server = mock_server_cls.return_value
            mock_server.serve_forever.side_effect = KeyboardInterrupt

            runner.invoke(main, ["preview", "--project-dir", str(project)])
            handler = mock_server_cls.call_args.args[1]
            assert handler.__name__ == "PreviewRequestHandler"
            assert not (build_dir / "index.html").exists()

    def test_preview_custom_port(self, runner, project):
        """Test --port option is accepted."""
        with patch("http.server.HTTPServer") as mock_server_cls:
            mock_server = mock_server_cls.return_value
            mock_server.serve_forever.side_effect = KeyboardInterrupt

            result = runner.invoke(
                main, ["preview", "--port", "0", "--project-dir", str(project)]
            )
            assert result.exit_code == 0

    def test_preview_version_flag(self, runner, project):
        """--version flag is accepted by the runtime handler."""
        build_dir = project / ".fdesign" / "projects" / "main" / "build"
        (build_dir / "home.html").write_text("<html></html>", encoding="utf-8")
        versions_dir = project / ".fdesign" / "projects" / "main" / "versions" / "v1.0"
        versions_dir.mkdir(parents=True)
        import json as _json
        (versions_dir / "meta.json").write_text(
            _json.dumps({"version": "v1.0", "message": "first", "created_at": "2026-01-01T00:00:00+00:00"}),
            encoding="utf-8",
        )
        with patch("http.server.HTTPServer") as mock_server_cls:
            mock_server = mock_server_cls.return_value
            mock_server.serve_forever.side_effect = KeyboardInterrupt

            result = runner.invoke(
                main, ["preview", "--version", "v1.0", "--project-dir", str(project)]
            )
            assert result.exit_code == 0
            handler = mock_server_cls.call_args.args[1]
            assert handler.__name__ == "PreviewRequestHandler"
            assert not (build_dir / "index.html").exists()

    def test_preview_url_uses_root_path(self, runner, project):
        """URL printed points at the virtual preview index."""
        with patch("http.server.HTTPServer") as mock_server_cls:
            mock_server = mock_server_cls.return_value
            mock_server.serve_forever.side_effect = KeyboardInterrupt

            result = runner.invoke(main, ["preview", "--project-dir", str(project)])
            assert "http://127.0.0.1:" in result.output
            assert "/build/" not in result.output

# ---------------------------------------------------------------------------
# fdesign prd / sitemap / component
# ---------------------------------------------------------------------------


class TestPrototypeSourceCommands:
    def test_prd_init_validate_and_duplicate(self, runner, project):
        init = runner.invoke(main, ["prd", "init", "--project-dir", str(project)])
        assert init.exit_code == 0
        assert "prd.md" in init.output

        duplicate = runner.invoke(main, ["prd", "init", "--project-dir", str(project)])
        assert duplicate.exit_code != 0
        assert "already exists" in duplicate.output

        prd_path = project / ".fdesign" / "projects" / "main" / "prd.md"
        prd_path.write_text(
            """\
---
version: 1
updated_at: 2024-01-01
product: Demo
target_users:
  - user
core_flows:
  - login
css_framework: tailwind
status: confirmed
---
body
""",
            encoding="utf-8",
        )
        validate = runner.invoke(main, ["prd", "validate", "--project-dir", str(project)])
        assert validate.exit_code == 0
        assert "valid" in validate.output

    def test_prd_validate_reports_errors(self, runner, project):
        prd_path = project / ".fdesign" / "projects" / "main" / "prd.md"
        prd_path.write_text("---\nproduct: Demo\n---\n", encoding="utf-8")
        result = runner.invoke(main, ["prd", "validate", "--project-dir", str(project)])
        assert result.exit_code != 0
        assert "target_users" in result.output

    def test_sitemap_init_validate_and_duplicate(self, runner, project):
        init = runner.invoke(main, ["sitemap", "init", "--project-dir", str(project)])
        assert init.exit_code == 0
        assert "sitemap.md" in init.output

        duplicate = runner.invoke(main, ["sitemap", "init", "--project-dir", str(project)])
        assert duplicate.exit_code != 0
        assert "already exists" in duplicate.output

        sitemap_path = project / ".fdesign" / "projects" / "main" / "sitemap.md"
        sitemap_path.write_text(
            """\
---
version: 1
updated_at: 2024-01-01
pages:
  - id: home
    title: Home
    file: build/home.html
    status: planned
---
body
""",
            encoding="utf-8",
        )
        validate = runner.invoke(main, ["sitemap", "validate", "--project-dir", str(project)])
        assert validate.exit_code == 0
        assert "valid" in validate.output

    def test_sitemap_validate_reports_errors(self, runner, project):
        sitemap_path = project / ".fdesign" / "projects" / "main" / "sitemap.md"
        sitemap_path.write_text("---\npages: []\n---\n", encoding="utf-8")
        result = runner.invoke(main, ["sitemap", "validate", "--project-dir", str(project)])
        assert result.exit_code != 0
        assert "non-empty list" in result.output

    def test_component_init_validate_and_duplicate(self, runner, project):
        init = runner.invoke(main, ["component", "init", "--project-dir", str(project)])
        assert init.exit_code == 0
        assert "components.yaml" in init.output

        duplicate = runner.invoke(main, ["component", "init", "--project-dir", str(project)])
        assert duplicate.exit_code != 0
        assert "already exists" in duplicate.output

        components_path = project / ".fdesign" / "projects" / "main" / "components.yaml"
        components_path.write_text(
            """\
version: 1
updated_at: 2024-01-01
css_framework: tailwind
components:
  - id: navbar
    title: Nav
    status: draft
    tokens:
      background: color.surface
""",
            encoding="utf-8",
        )
        validate = runner.invoke(main, ["component", "validate", "--project-dir", str(project)])
        assert validate.exit_code == 0
        assert "valid" in validate.output

    def test_component_validate_reports_errors(self, runner, project):
        components_path = project / ".fdesign" / "projects" / "main" / "components.yaml"
        components_path.write_text("components: []\n", encoding="utf-8")
        result = runner.invoke(main, ["component", "validate", "--project-dir", str(project)])
        assert result.exit_code != 0
        assert "components list is empty" in result.output


# ---------------------------------------------------------------------------
# fdesign version / journey
# ---------------------------------------------------------------------------


class TestVersionAndJourneyCommand:
    def test_version_create_and_list(self, runner, project):
        build_dir = project / ".fdesign" / "projects" / "main" / "build"
        (build_dir / "journey").mkdir()
        (build_dir / "journey" / "home.html").write_text("<html></html>", encoding="utf-8")

        create = runner.invoke(
            main,
            ["version", "create", "v1.0", "-m", "first", "--project-dir", str(project)],
        )
        assert create.exit_code == 0
        assert "v1.0" in create.output

        duplicate = runner.invoke(main, ["version", "create", "v1.0", "--project-dir", str(project)])
        assert duplicate.exit_code != 0
        assert "already exists" in duplicate.output

        listing = runner.invoke(main, ["version", "list", "--project-dir", str(project)])
        assert listing.exit_code == 0
        assert "first" in listing.output

    def test_version_create_requires_build_and_list_empty(self, runner, project):
        listing = runner.invoke(main, ["version", "list", "--project-dir", str(project)])
        assert listing.exit_code == 0
        assert "No versions found" in listing.output

        shutil.rmtree(project / ".fdesign" / "projects" / "main" / "build")
        create = runner.invoke(main, ["version", "create", "v1.0", "--project-dir", str(project)])
        assert create.exit_code != 0
        assert "build" in create.output

    def test_journey_check_passes_and_fails(self, runner, project):
        html_file = project / ".fdesign" / "projects" / "main" / "build" / "journey" / "home.html"
        html_file.parent.mkdir(parents=True)
        html_file.write_text(
            '<html><head><link rel="stylesheet" href="../tokens/tokens.css">'
            '<script src="../components.js"></script></head>'
            '<body><cv-button data-component="button">Save</cv-button></body></html>',
            encoding="utf-8",
        )
        tokens_dir = project / ".fdesign" / "projects" / "main" / "tokens"
        (tokens_dir / "global.tokens.json").write_text('{"color":{"$type":"color","$value":"#000"}}', encoding="utf-8")
        components = project / ".fdesign" / "projects" / "main" / "components.yaml"
        components.write_text(
            "version: 1\nupdated_at: 2024-01-01\ncss_framework: tailwind\ncomponents:\n"
            "  - id: button\n    title: Button\n    status: built\n    html_tag: cv-button\n",
            encoding="utf-8",
        )
        result = runner.invoke(main, ["journey", "check", str(html_file), "--project-dir", str(project)])
        assert result.exit_code == 0
        assert "passed" in result.output

        html_file.write_text("<html><body><div>Raw</div></body></html>", encoding="utf-8")
        result = runner.invoke(main, ["journey", "check", str(html_file), "--project-dir", str(project)])
        assert result.exit_code != 0
        assert "error" in result.output
