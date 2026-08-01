"""fdesign CLI entry point."""

import json
import os
from pathlib import Path

import click

from fdesign import __version__
from fdesign.adapters import (
    ADAPTERS,
    SUPPORTED_AGENTS,
)
from fdesign.project import (
    ProjectError,
    create_project,
    init_workspace,
    list_projects,
    resolve_project,
)


def _resolve_floop_project(project_dir: Path, project: str | None) -> Path:
    """Resolve a CLI workspace/project pair to a fdesign project path."""
    try:
        return resolve_project(project_dir.resolve(), project).path
    except ProjectError as exc:
        click.secho(f"⚠ {exc}", fg="yellow", err=True)
        raise SystemExit(1) from exc


@click.group()
@click.version_option(__version__, prog_name="fdesign")
def main():
    """fdesign — token and component governed prototype toolkit.

    \b
    Quick start:
      fdesign init              Initialize a fdesign project
      fdesign enable copilot    Install skills (GitHub Copilot)
      fdesign enable cursor     Install skills (Cursor)
      fdesign enable claude     Install skills (Claude Code)
      fdesign enable trae       Install skills (Trae IDE)
      fdesign enable codex      Install skills (Codex)
      fdesign enable qwen-code  Install skills (Qwen Code)
      fdesign enable opencode   Install skills (OpenCode)
      fdesign enable openclaw   Install skills (OpenClaw)
    """


@main.command()
@click.option(
    "--project-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=".",
    help="Workspace root directory (default: current directory).",
)
def init(project_dir: Path):
    """Initialize a fdesign project.

    Creates a .fdesign/ workspace skeleton. Use 'fdesign project create <name>'
    to add projects on demand.
    """
    project_dir = project_dir.resolve()
    floop_dir = project_dir / ".fdesign"

    if floop_dir.exists():
        click.secho("⚠ .fdesign/ already exists, skipping initialization.", fg="yellow")
        return

    init_workspace(project_dir)

    click.secho("✓ fdesign workspace initialized", fg="green", bold=True)
    click.echo(f"  .fdesign/config.json")
    click.echo(f"  .fdesign/projects.csv")
    click.echo(f"  .fdesign/projects/")


@main.command()
@click.argument("agent", type=click.Choice(SUPPORTED_AGENTS, case_sensitive=False))
@click.option(
    "--project-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=".",
    help="Project root directory (default: current directory).",
)
def enable(agent: str, project_dir: Path):
    """Install fdesign skills into an AI agent platform.

    \b
    Supported agents:
      copilot    GitHub Copilot (VS Code) — .github/skills/ + .github/instructions/
      cursor     Cursor — .cursor/rules/
      claude     Claude Code — .claude/skills/ + CLAUDE.md
      trae       Trae IDE — .trae/project_rules.md
      codex      Codex — .codex/skills/ + AGENTS.md
      qwen-code  Qwen Code (CLI) — AGENTS.md
      opencode   OpenCode (CLI) — .opencode/skills/ + AGENTS.md
      openclaw   OpenClaw — .openclaw/skills/ + AGENTS.md
    """
    project_dir = project_dir.resolve()
    adapter = ADAPTERS[agent]()
    created = adapter.install(project_dir)

    click.secho(f"✓ fdesign skills installed for {agent}", fg="green", bold=True)
    for path in created:
        rel = path.relative_to(project_dir)
        click.echo(f"  {rel}")


# ---------------------------------------------------------------------------
# fdesign project — Workspace project management
# ---------------------------------------------------------------------------


@main.group()
def project():
    """Manage projects inside the .fdesign workspace."""


@project.command("list")
@click.option(
    "--project-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=".",
    help="Workspace root directory (default: current directory).",
)
@click.option("--json-output", is_flag=True, default=False)
def project_list_cmd(project_dir: Path, json_output: bool):
    """List projects in the .fdesign workspace."""
    project_dir = project_dir.resolve()
    try:
        projects = list_projects(project_dir)
    except ProjectError as exc:
        click.secho(f"⚠ {exc}", fg="yellow", err=True)
        raise SystemExit(1) from exc

    rows = [
        {
            "name": item.name,
            "title": item.title,
            "path": str(item.path.relative_to(project_dir)),
        }
        for item in projects
    ]
    if json_output:
        click.echo(json.dumps({"projects": rows}, indent=2, ensure_ascii=False))
        return
    if not rows:
        click.echo("No projects found. Run 'fdesign project create <name>'.")
        return
    for row in rows:
        suffix = f"  {row['title']}" if row["title"] and row["title"] != row["name"] else ""
        click.echo(f"  {row['name']}{suffix}")


@project.command("create")
@click.argument("name")
@click.option("--title", default="", help="Human-readable project title.")
@click.option(
    "--project-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=".",
    help="Workspace root directory (default: current directory).",
)
def project_create_cmd(name: str, title: str, project_dir: Path):
    """Create a project inside the .fdesign workspace."""
    project_dir = project_dir.resolve()
    try:
        created = create_project(
            project_dir,
            name,
            title=title or None,
        )
    except (ProjectError, FileExistsError) as exc:
        click.secho(f"⚠ {exc}", fg="yellow", err=True)
        raise SystemExit(1) from exc
    click.secho(f"✓ Project '{created.name}' created", fg="green", bold=True)
    click.echo(f"  {created.path.relative_to(project_dir)}")


@project.command("info")
@click.option("--project", "project_name", default=None, help="Project name.")
@click.option(
    "--project-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=".",
    help="Workspace root directory (default: current directory).",
)
def project_info_cmd(project_name: str | None, project_dir: Path):
    """Show resolved project paths."""
    project_dir = project_dir.resolve()
    try:
        item = resolve_project(project_dir, project_name)
    except ProjectError as exc:
        click.secho(f"⚠ {exc}", fg="yellow", err=True)
        raise SystemExit(1) from exc
    click.echo(f"name: {item.name}")
    click.echo(f"title: {item.title}")
    click.echo(f"path: {item.path.relative_to(project_dir)}")
    click.echo(f"content: {item.prototype_dir.relative_to(project_dir)}")


# ---------------------------------------------------------------------------
# fdesign token — Design Token management (W3C DTCG)
# ---------------------------------------------------------------------------


@main.group()
def token():
    """Manage design tokens (W3C DTCG format).

    \b
    Commands:
      fdesign token init       Generate default token files
      fdesign token validate   Validate token files
      fdesign token view       Generate HTML preview page
    """


@token.command("init")
@click.option("--project", "project_name", default=None, help="fdesign project name.")
@click.option(
    "--project-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=".",
    help="Workspace root directory (default: current directory).",
)
@click.option(
    "--force",
    is_flag=True,
    default=False,
    help="Overwrite existing token files.",
)
def token_init_cmd(project_name: str | None, project_dir: Path, force: bool):
    """Generate W3C DTCG token template files.

    Creates three files in the selected project's tokens/:
      global.tokens.json     Primitive design values
      semantic.tokens.json   Semantic aliases
      component.tokens.json  Component-level tokens
    """
    from fdesign.tokens import token_init

    workspace = project_dir.resolve()
    floop_project = _resolve_floop_project(workspace, project_name)
    tokens_dir = floop_project / "tokens"

    existing = list(tokens_dir.glob("*.tokens.json"))
    if existing and not force:
        click.secho(
            "⚠ Token files already exist. Use --force to overwrite.", fg="yellow"
        )
        return

    created = token_init(tokens_dir)

    click.secho("✓ Token files generated (W3C DTCG format)", fg="green", bold=True)
    for path in created:
        rel = path.relative_to(workspace)
        click.echo(f"  {rel}")


@token.command("validate")
@click.option("--project", "project_name", default=None, help="fdesign project name.")
@click.option(
    "--project-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=".",
    help="Workspace root directory (default: current directory).",
)
@click.option(
    "--json-output",
    "output_json",
    is_flag=True,
    default=False,
    help="Output structured JSON (for Agent consumption).",
)
def token_validate_cmd(project_name: str | None, project_dir: Path, output_json: bool):
    """Validate design token files against W3C DTCG spec.

    \b
    Three validation layers:
      L1  Format compliance (valid JSON, valid $type/$value)
      L2  Reference integrity (broken refs, circular deps)
      L3  Design suggestions (recommended semantic tokens)
    """
    from fdesign.tokens import token_validate

    workspace = project_dir.resolve()
    floop_project = _resolve_floop_project(workspace, project_name)
    tokens_dir = floop_project / "tokens"

    result = token_validate(tokens_dir)

    if output_json:
        click.echo(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        # Human-readable output
        stats = result["stats"]
        click.echo(
            f"Checked {stats['files']} file(s): "
            f"{stats['tokens']} tokens, "
            f"{stats['references']} references, "
            f"{stats['groups']} groups"
        )

        for err in result["errors"]:
            loc = err["path"] or err["file"]
            click.secho(f"  ✗ [{err['code']}] {loc}: {err['message']}", fg="red")
            if err.get("suggestion"):
                click.echo(f"    → {err['suggestion']}")

        for warn in result["warnings"]:
            loc = warn["path"] or warn["file"]
            click.secho(
                f"  ⚠ [{warn['code']}] {loc}: {warn['message']}", fg="yellow"
            )
            if warn.get("suggestion"):
                click.echo(f"    → {warn['suggestion']}")

        if result["valid"]:
            click.secho("✓ All tokens valid", fg="green", bold=True)
        else:
            click.secho(
                f"✗ {len(result['errors'])} error(s) found",
                fg="red",
                bold=True,
            )
            raise SystemExit(1)


@token.command("view")
@click.option("--project", "project_name", default=None, help="fdesign project name.")
@click.option(
    "--project-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=".",
    help="Workspace root directory (default: current directory).",
)
def token_view_cmd(project_name: str | None, project_dir: Path):
    """Generate an HTML preview page for design tokens.

    Reads all .tokens.json files, resolves references, and generates
    a visual preview at .fdesign/build/design-tokens.html.
    """
    from fdesign.tokens import token_view

    workspace = project_dir.resolve()
    floop_project = _resolve_floop_project(workspace, project_name)
    tokens_dir = floop_project / "tokens"

    if not tokens_dir.exists():
        click.secho(
            "⚠ tokens/ not found. Run 'fdesign init' and 'fdesign token init' first.",
            fg="yellow",
            err=True,
        )
        raise SystemExit(1)

    token_files = list(tokens_dir.glob("*.tokens.json"))
    if not token_files:
        click.secho(
            "⚠ No .tokens.json files found. Run 'fdesign token init' first.",
            fg="yellow",
            err=True,
        )
        raise SystemExit(1)

    build_dir = floop_project / "build" / "tokens"
    build_dir.mkdir(parents=True, exist_ok=True)
    out_path = token_view(tokens_dir, out_dir=build_dir)
    css_path = build_dir / "tokens.css"
    click.secho("✓ Token preview generated", fg="green", bold=True)
    click.echo(f"  {out_path.relative_to(workspace)}")
    click.echo(f"  {css_path.relative_to(workspace)}")


# ---------------------------------------------------------------------------
# fdesign preview — Local preview server
# ---------------------------------------------------------------------------


@main.command()
@click.option(
    "--project-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=".",
    help="Workspace root directory (default: current directory).",
)
@click.option("--project", "project_name", default=None, help="fdesign project name.")
@click.option(
    "--view",
    type=click.Choice(["prototype"], case_sensitive=False),
    default="prototype",
    help="Prototype view to preview.",
)
@click.option(
    "--port",
    type=int,
    default=0,
    help="Port number (default: auto-assign a free port).",
)
@click.option(
    "--version",
    "active_version",
    default="trunk",
    help="Version to preview (default: trunk = current build).",
)
def preview(project_name: str | None, view: str, project_dir: Path, port: int, active_version: str):
    """Start a local web server to preview fdesign output.

    Renders a navigation index page at request time and serves it on
    a temporary local port. Open the printed URL in your browser to
    browse design tokens, components, and prototype pages.

    Use --version to start preview pinned to a named snapshot.

    Press Ctrl+C to stop the server.
    """
    import http.server

    from fdesign.preview import create_preview_request_handler

    workspace = project_dir.resolve()
    floop_project = _resolve_floop_project(workspace, project_name)
    build_dir = floop_project / "build"
    build_dir.mkdir(parents=True, exist_ok=True)

    # Serve from the selected project so build/ and versions/ are reachable.
    # The preview index is virtual and is not written into build/.
    handler = create_preview_request_handler(
        floop_project,
        build_dir,
        active_version=active_version,
    )

    server = http.server.HTTPServer(("127.0.0.1", port), handler)
    address = getattr(server, "server_address", None)
    chosen_port = address[1] if isinstance(address, tuple) else port

    click.secho("fdesign preview server", fg="green", bold=True)
    click.echo(f"  project: {floop_project.name}")
    click.echo(f"  view: {view}")
    click.echo(f"  http://127.0.0.1:{chosen_port}/")
    click.echo("\n  Press Ctrl+C to stop.\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        click.echo("\nServer stopped.")


# ---------------------------------------------------------------------------
# fdesign prd — Product Requirements Document management
# ---------------------------------------------------------------------------


@main.group()
def prd():
    """Manage product requirements document (prd.md).

    \b
    Commands:
      fdesign prd init       Create prd.md template
      fdesign prd validate   Validate prd.md frontmatter
    """


@prd.command("init")
@click.option("--project", "project_name", default=None, help="fdesign project name.")
@click.option(
    "--project-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=".",
    help="Workspace root directory (default: current directory).",
)
def prd_init_cmd(project_name: str | None, project_dir: Path):
    """Create prd.md from template.

    Generates a PRD document with YAML frontmatter (product, target_users,
    core_flows, css_framework, status) and Markdown sections for you to fill in.
    """
    from fdesign.prototype import prd_init

    workspace = project_dir.resolve()
    floop_project = _resolve_floop_project(workspace, project_name)
    try:
        path = prd_init(floop_project)
    except FileExistsError as exc:
        click.secho(f"⚠ {exc}", fg="yellow", err=True)
        raise SystemExit(1)

    rel = path.relative_to(workspace)
    click.secho("✓ prd.md created", fg="green", bold=True)
    click.echo(f"  {rel}")


@prd.command("validate")
@click.option("--project", "project_name", default=None, help="fdesign project name.")
@click.option(
    "--project-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=".",
    help="Workspace root directory (default: current directory).",
)
def prd_validate_cmd(project_name: str | None, project_dir: Path):
    """Validate prd.md frontmatter fields."""
    from fdesign.prototype import prd_validate

    workspace = project_dir.resolve()
    floop_project = _resolve_floop_project(workspace, project_name)
    errors, warnings = prd_validate(floop_project)

    for warn in warnings:
        click.secho(f"  ⚠ {warn}", fg="yellow")
    for err in errors:
        click.secho(f"  ✗ {err}", fg="red")

    if errors:
        click.secho(f"✗ {len(errors)} error(s) found", fg="red", bold=True)
        raise SystemExit(1)

    click.secho("✓ prd.md is valid", fg="green", bold=True)


# ---------------------------------------------------------------------------
# fdesign sitemap — Sitemap management
# ---------------------------------------------------------------------------


@main.group()
def sitemap():
    """Manage sitemap definition (sitemap.md).

    \b
    Commands:
      fdesign sitemap init       Create sitemap.md template
      fdesign sitemap validate   Validate sitemap.md frontmatter
    """


@sitemap.command("init")
@click.option("--project", "project_name", default=None, help="fdesign project name.")
@click.option(
    "--project-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=".",
    help="Workspace root directory (default: current directory).",
)
def sitemap_init_cmd(project_name: str | None, project_dir: Path):
    """Create sitemap.md from template.

    Generates a sitemap document with YAML frontmatter listing pages
    (id, title, file, status) for you to fill in.
    """
    from fdesign.prototype import sitemap_init

    workspace = project_dir.resolve()
    floop_project = _resolve_floop_project(workspace, project_name)
    try:
        path = sitemap_init(floop_project)
    except FileExistsError as exc:
        click.secho(f"⚠ {exc}", fg="yellow", err=True)
        raise SystemExit(1)

    rel = path.relative_to(workspace)
    click.secho("✓ sitemap.md created", fg="green", bold=True)
    click.echo(f"  {rel}")


@sitemap.command("validate")
@click.option("--project", "project_name", default=None, help="fdesign project name.")
@click.option(
    "--project-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=".",
    help="Workspace root directory (default: current directory).",
)
def sitemap_validate_cmd(project_name: str | None, project_dir: Path):
    """Validate sitemap.md frontmatter fields."""
    from fdesign.prototype import sitemap_validate

    workspace = project_dir.resolve()
    floop_project = _resolve_floop_project(workspace, project_name)
    errors, warnings = sitemap_validate(floop_project)

    for warn in warnings:
        click.secho(f"  ⚠ {warn}", fg="yellow")
    for err in errors:
        click.secho(f"  ✗ {err}", fg="red")

    if errors:
        click.secho(f"✗ {len(errors)} error(s) found", fg="red", bold=True)
        raise SystemExit(1)

    click.secho("✓ sitemap.md is valid", fg="green", bold=True)


# ---------------------------------------------------------------------------
# fdesign component — Component library management
# ---------------------------------------------------------------------------


@main.group()
def component():
    """Manage component library definition (components.yaml).

    \b
    Commands:
      fdesign component init       Create components.yaml template
      fdesign component validate   Validate components.yaml
    """


@component.command("init")
@click.option("--project", "project_name", default=None, help="fdesign project name.")
@click.option(
    "--project-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=".",
    help="Workspace root directory (default: current directory).",
)
def component_init_cmd(project_name: str | None, project_dir: Path):
    """Create components.yaml from template.

    Generates a component library file with YAML structure
    (id, title, status, tokens) for you to fill in.
    """
    from fdesign.prototype import component_init

    workspace = project_dir.resolve()
    floop_project = _resolve_floop_project(workspace, project_name)
    try:
        path = component_init(floop_project)
    except FileExistsError as exc:
        click.secho(f"⚠ {exc}", fg="yellow", err=True)
        raise SystemExit(1)

    rel = path.relative_to(workspace)
    click.secho("✓ components.yaml created", fg="green", bold=True)
    click.echo(f"  {rel}")


@component.command("validate")
@click.option("--project", "project_name", default=None, help="fdesign project name.")
@click.option(
    "--project-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=".",
    help="Workspace root directory (default: current directory).",
)
def component_validate_cmd(project_name: str | None, project_dir: Path):
    """Validate components.yaml fields."""
    from fdesign.prototype import component_validate

    workspace = project_dir.resolve()
    floop_project = _resolve_floop_project(workspace, project_name)
    errors, warnings = component_validate(floop_project)

    for warn in warnings:
        click.secho(f"  ⚠ {warn}", fg="yellow")
    for err in errors:
        click.secho(f"  ✗ {err}", fg="red")

    if errors:
        click.secho(f"✗ {len(errors)} error(s) found", fg="red", bold=True)
        raise SystemExit(1)

    click.secho("✓ components.yaml is valid", fg="green", bold=True)


# ---------------------------------------------------------------------------
# fdesign prototype — Journey Map management
# ---------------------------------------------------------------------------


@main.group()
def prototype():
    """Manage prototype journey map (journey-map.csv).

    \b
    Commands:
      fdesign prototype init       Build journey-map.csv from sitemap.md
      fdesign prototype validate   Validate journey HTMLs against journey-map.csv
    """


@prototype.command("init")
@click.option("--project", "project_name", default=None, help="fdesign project name.")
@click.option(
    "--project-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=".",
    help="Workspace root directory (default: current directory).",
)
def prototype_init_cmd(project_name: str | None, project_dir: Path):
    """Build journey-map.csv from sitemap.md.

    Reads all pages in sitemap.md frontmatter and generates a CSV mapping
    sitemap domains to HTML files.  The domain is taken from each page's
    optional 'domain' field; if absent it is derived from the file path
    (e.g. build/journey/auth/login.html → domain 'auth').

    The CSV is always regenerated — safe to re-run after updating sitemap.md.
    """
    from fdesign.prototype import prototype_init

    workspace = project_dir.resolve()
    floop_project = _resolve_floop_project(workspace, project_name)
    try:
        path = prototype_init(floop_project)
    except FileNotFoundError as exc:
        click.secho(f"⚠ {exc}", fg="yellow", err=True)
        raise SystemExit(1)

    rel = path.relative_to(workspace)
    click.secho("✓ journey-map.csv generated", fg="green", bold=True)
    click.echo(f"  {rel}")


@prototype.command("validate")
@click.option("--project", "project_name", default=None, help="fdesign project name.")
@click.option(
    "--project-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=".",
    help="Workspace root directory (default: current directory).",
)
def prototype_validate_cmd(project_name: str | None, project_dir: Path):
    """Validate journey HTML files against journey-map.csv and sitemap.md.

    \b
    Two checks:
      1. Every HTML under build/journey/ is mapped in journey-map.csv
      2. Every domain in journey-map.csv exists in sitemap.md pages
    """
    from fdesign.prototype import prototype_validate

    workspace = project_dir.resolve()
    floop_project = _resolve_floop_project(workspace, project_name)
    errors, warnings = prototype_validate(floop_project)

    for warn in warnings:
        click.secho(f"  ⚠ {warn}", fg="yellow")
    for err in errors:
        click.secho(f"  ✗ {err}", fg="red")

    if errors:
        click.secho(f"✗ {len(errors)} error(s) found", fg="red", bold=True)
        raise SystemExit(1)

    click.secho("✓ prototype is valid", fg="green", bold=True)


# ---------------------------------------------------------------------------
# fdesign locale — Prototype localization catalog management
# ---------------------------------------------------------------------------


@main.group()
def locale():
    """Manage prototype localization catalogs.

    \b
    Commands:
      fdesign locale init --source en  Initialize a source catalog
      fdesign locale add fr_FR          Scaffold a translation catalog
      fdesign locale remove fr_FR       Remove a translation catalog
      fdesign locale list               List configured catalogs
      fdesign locale validate           Validate catalog consistency
    """


def _locale_project(project_dir: Path, project_name: str | None) -> tuple[Path, Path]:
    workspace = project_dir.resolve()
    return workspace, _resolve_floop_project(workspace, project_name)


@locale.command("init")
@click.option("--source", "source_locale", required=True, help="Source locale identifier.")
@click.option("--project", "project_name", default=None, help="fdesign project name.")
@click.option("--project-dir", type=click.Path(exists=True, file_okay=False, path_type=Path), default=".")
def locale_init_cmd(source_locale: str, project_name: str | None, project_dir: Path):
    """Initialize the source locale catalog."""
    from fdesign.prototype import locale_init

    workspace, floop_project = _locale_project(project_dir, project_name)
    try:
        path = locale_init(floop_project, source_locale)
    except (FileExistsError, ValueError) as exc:
        click.secho(f"⚠ {exc}", fg="yellow", err=True)
        raise SystemExit(1) from exc
    click.secho("✓ locale source catalog initialized", fg="green", bold=True)
    click.echo(f"  {path.relative_to(workspace)}")


@locale.command("add")
@click.argument("locale_name")
@click.option("--project", "project_name", default=None, help="fdesign project name.")
@click.option("--project-dir", type=click.Path(exists=True, file_okay=False, path_type=Path), default=".")
def locale_add_cmd(locale_name: str, project_name: str | None, project_dir: Path):
    """Scaffold a translation catalog from the source key inventory."""
    from fdesign.prototype import locale_add

    workspace, floop_project = _locale_project(project_dir, project_name)
    try:
        path = locale_add(floop_project, locale_name)
    except (FileExistsError, FileNotFoundError, ValueError) as exc:
        click.secho(f"⚠ {exc}", fg="yellow", err=True)
        raise SystemExit(1) from exc
    click.secho(f"✓ locale '{locale_name}' added", fg="green", bold=True)
    click.echo(f"  {path.relative_to(workspace)}")


@locale.command("remove")
@click.argument("locale_name")
@click.option("--project", "project_name", default=None, help="fdesign project name.")
@click.option("--project-dir", type=click.Path(exists=True, file_okay=False, path_type=Path), default=".")
def locale_remove_cmd(locale_name: str, project_name: str | None, project_dir: Path):
    """Remove a non-source translation catalog."""
    from fdesign.prototype import locale_remove

    workspace, floop_project = _locale_project(project_dir, project_name)
    try:
        path = locale_remove(floop_project, locale_name)
    except (FileNotFoundError, ValueError) as exc:
        click.secho(f"⚠ {exc}", fg="yellow", err=True)
        raise SystemExit(1) from exc
    click.secho(f"✓ locale '{locale_name}' removed", fg="green", bold=True)
    click.echo(f"  {path.relative_to(workspace)}")


@locale.command("list")
@click.option("--project", "project_name", default=None, help="fdesign project name.")
@click.option("--project-dir", type=click.Path(exists=True, file_okay=False, path_type=Path), default=".")
def locale_list_cmd(project_name: str | None, project_dir: Path):
    """List available locale catalogs."""
    from fdesign.prototype import locale_list

    _, floop_project = _locale_project(project_dir, project_name)
    catalogs, errors = locale_list(floop_project)
    for error in errors:
        click.secho(f"  ✗ {error}", fg="red")
    if errors:
        raise SystemExit(1)
    if not catalogs:
        click.echo("No locale catalogs found. Run 'fdesign locale init --source <locale>'.")
        return
    for locale_name in catalogs:
        click.echo(f"  {locale_name}")


@locale.command("validate")
@click.option("--project", "project_name", default=None, help="fdesign project name.")
@click.option("--project-dir", type=click.Path(exists=True, file_okay=False, path_type=Path), default=".")
def locale_validate_cmd(project_name: str | None, project_dir: Path):
    """Validate locale catalog format, keys, and placeholders."""
    from fdesign.prototype import locale_validate

    _, floop_project = _locale_project(project_dir, project_name)
    errors = locale_validate(floop_project)
    for error in errors:
        click.secho(f"  ✗ {error}", fg="red")
    if errors:
        click.secho(f"✗ {len(errors)} error(s) found", fg="red", bold=True)
        raise SystemExit(1)
    click.secho("✓ locale catalogs are valid", fg="green", bold=True)


# ---------------------------------------------------------------------------
# fdesign version — Trunk-based prototype version snapshots
# ---------------------------------------------------------------------------


@main.group()
def version():
    """Manage project versions (trunk-based snapshots).

    \b
    Commands:
      fdesign version create   Snapshot current build into a named version
      fdesign version list     List all versions
    """


@version.command("create")
@click.argument("name")
@click.option("-m", "--message", default="", help="Version description.")
@click.option("--project", "project_name", default=None, help="fdesign project name.")
@click.option(
    "--project-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=".",
    help="Workspace root directory (default: current directory).",
)
def version_create_cmd(name: str, message: str, project_name: str | None, project_dir: Path):
    """Snapshot build/ into project versions/NAME/.

    NAME must be unique (e.g. v1.0, v1.1-homepage-revamp).
    Always run this before sharing a build with a client.
    """
    from fdesign.prototype import version_create

    workspace = project_dir.resolve()
    floop_project = _resolve_floop_project(workspace, project_name)

    try:
        version_dir = version_create(floop_project, name, message)
    except (ValueError, FileNotFoundError) as exc:
        click.secho(f"⚠ {exc}", fg="yellow", err=True)
        raise SystemExit(1)

    rel = version_dir.relative_to(workspace)
    click.secho(f"✓ Version '{name}' created", fg="green", bold=True)
    click.echo(f"  {rel}")


@version.command("list")
@click.option("--project", "project_name", default=None, help="fdesign project name.")
@click.option(
    "--project-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=".",
    help="Workspace root directory (default: current directory).",
)
def version_list_cmd(project_name: str | None, project_dir: Path):
    """List all project versions."""
    from fdesign.prototype import version_list

    workspace = project_dir.resolve()
    floop_project = _resolve_floop_project(workspace, project_name)
    versions = version_list(floop_project)

    if not versions:
        click.echo("No versions found. Run 'fdesign version create' to create one.")
        return

    for v in versions:
        date = v.get("created_at", "")[:10]
        msg = v.get("message", "")
        suffix = f"  {msg}" if msg else ""
        click.echo(f"  {v['version']}  ({date}){suffix}")


# ---------------------------------------------------------------------------
# fdesign journey — Journey backward-check commands
# ---------------------------------------------------------------------------


@main.group()
def journey():
    """Manage journey HTML pages.

    \b
    Commands:
      fdesign journey check   Backward-check a journey HTML for token/component gaps
    """


@journey.command("check")
@click.argument(
    "html_file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
)
@click.option("--project", "project_name", default=None, help="fdesign project name.")
@click.option(
    "--project-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=".",
    help="Workspace root directory (default: current directory).",
)
def journey_check_cmd(html_file: Path, project_name: str | None, project_dir: Path):
    """Backward-check a journey HTML file for token and component gaps.

    Scans HTML_FILE for missing token references, unused components,
    and missing head links (tokens.css / components.js).
    """
    from fdesign.prototype import journey_check

    workspace = project_dir.resolve()
    floop_project = _resolve_floop_project(workspace, project_name)
    html_file = html_file.resolve()
    errors, warnings = journey_check(floop_project, html_file)

    for warn in warnings:
        click.secho(f"  ⚠ {warn}", fg="yellow")
    for err in errors:
        click.secho(f"  ✗ {err}", fg="red")

    if errors:
        click.secho(
            f"✗ {len(errors)} error(s) found", fg="red", bold=True
        )
        raise SystemExit(1)

    click.secho("✓ journey check passed", fg="green", bold=True)


if __name__ == "__main__":
    main()  # pragma: no cover
