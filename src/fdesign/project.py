"""fdesign workspace project model.

`.fdesign/` is a workspace root. Work happens directly inside named projects
under `.fdesign/projects/<project>/`.
"""

from __future__ import annotations

import csv
import datetime
import json
import re
from dataclasses import dataclass
from pathlib import Path

from fdesign import __version__

PROJECTS_CSV = "projects.csv"


class ProjectError(RuntimeError):
    """Raised for user-actionable project workspace failures."""


@dataclass(frozen=True)
class FloopProject:
    """A named project inside a fdesign workspace."""

    name: str
    path: Path
    title: str = ""

    @property
    def prototype_dir(self) -> Path:
        return self.path

    @property
    def versions_dir(self) -> Path:
        return self.path / "versions"


def slugify_project_name(name: str) -> str:
    """Return a filesystem-safe project id."""
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", name.strip().lower()).strip("-")
    if not slug:
        raise ProjectError("Project name cannot be empty.")
    return slug


def workspace_dir(project_dir: Path) -> Path:
    """Return the `.fdesign` workspace directory for a host project."""
    return project_dir / ".fdesign"


def projects_dir(project_dir: Path) -> Path:
    """Return the workspace projects directory."""
    return workspace_dir(project_dir) / "projects"


def projects_csv_path(project_dir: Path) -> Path:
    """Return the project index CSV path."""
    return workspace_dir(project_dir) / PROJECTS_CSV


def ensure_workspace(project_dir: Path) -> Path:
    """Return `.fdesign/`, raising if the workspace has not been initialized."""
    root = workspace_dir(project_dir)
    if not root.exists():
        raise ProjectError(".fdesign/ not found. Run 'fdesign init' first.")
    return root


def init_workspace(project_dir: Path) -> None:
    """Create a new fdesign workspace skeleton (no default project)."""
    root = workspace_dir(project_dir)
    if root.exists():
        raise FileExistsError(".fdesign/ already exists")

    root.mkdir(parents=True)
    (root / "config.json").write_text(
        json.dumps({"version": __version__, "schema": 2, "workspace": "fdesign"}, indent=2) + "\n",
        encoding="utf-8",
    )
    (root / ".gitignore").write_text(
        "# Generated prototypes\n/projects/*/build/\n",
        encoding="utf-8",
    )
    # Create empty projects directory — projects are created on demand
    (root / "projects").mkdir(parents=True)


def create_project(
    project_dir: Path,
    name: str,
    *,
    title: str | None = None,
) -> FloopProject:
    """Create a named project inside `.fdesign/projects/`."""
    root = ensure_workspace(project_dir)
    slug = slugify_project_name(name)
    path = projects_dir(project_dir) / slug
    if path.exists():
        raise FileExistsError(f"Project '{slug}' already exists.")

    for subdir in (
        path / "tokens",
        path / "build",
        path / "versions",
    ):
        subdir.mkdir(parents=True, exist_ok=True)

    project_title = title or slug
    metadata = {
        "version": 1,
        "name": slug,
        "title": project_title,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    (path / "project.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    _write_projects_index(project_dir, _read_projects_index(project_dir) + [metadata])
    return FloopProject(slug, path, project_title)


def list_projects(project_dir: Path) -> list[FloopProject]:
    """List fdesign projects from the project index and filesystem."""
    ensure_workspace(project_dir)
    rows = _read_projects_index(project_dir)
    seen: set[str] = set()
    projects: list[FloopProject] = []

    for row in rows:
        name = str(row.get("name", "")).strip()
        if not name or name in seen:
            continue
        path = projects_dir(project_dir) / name
        if path.exists():
            projects.append(
                FloopProject(
                    name=name,
                    path=path,
                    title=str(row.get("title") or name),
                )
            )
            seen.add(name)

    for path in sorted(projects_dir(project_dir).glob("*")):
        if path.is_dir() and path.name not in seen:
            meta = load_project_metadata(path)
            projects.append(
                FloopProject(
                    name=path.name,
                    path=path,
                    title=str(meta.get("title") or path.name),
                )
            )
            seen.add(path.name)

    return sorted(projects, key=lambda item: item.name)


def resolve_project(project_dir: Path, name: str | None = None) -> FloopProject:
    """Resolve a named project, or the sole project if omitted."""
    projects = list_projects(project_dir)
    if not projects:
        raise ProjectError("No fdesign projects found. Run 'fdesign project create <name>'.")

    if name:
        slug = slugify_project_name(name)
        for project in projects:
            if project.name == slug:
                return project
        raise ProjectError(f"Project '{slug}' not found.")

    if len(projects) == 1:
        return projects[0]
    raise ProjectError("Multiple fdesign projects found. Pass --project <name>.")


def load_project_metadata(project_path: Path) -> dict:
    """Load project.json metadata if present."""
    metadata_path = project_path / "project.json"
    if not metadata_path.exists():
        return {}
    try:
        return json.loads(metadata_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ProjectError(f"Invalid {metadata_path}: {exc}") from exc


def _read_projects_index(project_dir: Path) -> list[dict]:
    path = projects_csv_path(project_dir)
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _write_projects_index(project_dir: Path, rows: list[dict]) -> None:
    path = projects_csv_path(project_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["name", "title", "created_at"]
    deduped: dict[str, dict] = {}
    for row in rows:
        name = str(row.get("name", "")).strip()
        if name:
            deduped[name] = {field: str(row.get(field) or "") for field in fieldnames}
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(deduped.values())
