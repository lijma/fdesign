"""Tests for fdesign.project."""

import json

import pytest

from fdesign.project import (
    FloopProject,
    ProjectError,
    create_project,
    ensure_workspace,
    init_workspace,
    list_projects,
    load_project_metadata,
    projects_csv_path,
    projects_dir,
    resolve_project,
    slugify_project_name,
    workspace_dir,
)


def test_workspace_helpers(tmp_path):
    assert workspace_dir(tmp_path) == tmp_path / ".fdesign"
    assert projects_dir(tmp_path) == tmp_path / ".fdesign" / "projects"
    assert projects_csv_path(tmp_path) == tmp_path / ".fdesign" / "projects.csv"


def test_project_properties(tmp_path):
    project = FloopProject("demo", tmp_path / "demo")
    assert project.prototype_dir == tmp_path / "demo"
    assert project.versions_dir == tmp_path / "demo" / "versions"


def test_slugify_project_name():
    assert slugify_project_name(" Care Voice Demo ") == "care-voice-demo"
    assert slugify_project_name("A_B-1") == "a_b-1"
    with pytest.raises(ProjectError, match="empty"):
        slugify_project_name("   ")


def test_ensure_workspace_requires_init(tmp_path):
    with pytest.raises(ProjectError, match="fdesign init"):
        ensure_workspace(tmp_path)


def test_init_workspace_creates_skeleton(tmp_path):
    init_workspace(tmp_path)
    assert (tmp_path / ".fdesign" / "config.json").exists()
    assert "build" in (tmp_path / ".fdesign" / ".gitignore").read_text(encoding="utf-8")
    assert (tmp_path / ".fdesign" / "projects").is_dir()
    # No default project — projects are created on demand
    assert list_projects(tmp_path) == []


def test_init_workspace_rejects_existing_workspace(tmp_path):
    init_workspace(tmp_path)
    with pytest.raises(FileExistsError, match="already exists"):
        init_workspace(tmp_path)


def test_create_project_writes_metadata_and_index(tmp_path):
    init_workspace(tmp_path)
    project = create_project(
        tmp_path,
        "Sales Portal",
        title="Sales Portal",
    )
    metadata = json.loads((project.path / "project.json").read_text(encoding="utf-8"))
    assert metadata["name"] == "sales-portal"
    assert metadata["title"] == "Sales Portal"
    assert "sales-portal" in projects_csv_path(tmp_path).read_text(encoding="utf-8")


def test_create_project_rejects_missing_workspace_and_duplicate(tmp_path):
    with pytest.raises(ProjectError, match="fdesign init"):
        create_project(tmp_path, "demo")
    init_workspace(tmp_path)
    create_project(tmp_path, "my-project")
    with pytest.raises(FileExistsError, match="my-project"):
        create_project(tmp_path, "my-project")


def test_list_projects_uses_index_and_discovers_filesystem_projects(tmp_path):
    init_workspace(tmp_path)
    create_project(tmp_path, "main")
    orphan = projects_dir(tmp_path) / "orphan"
    orphan.mkdir(parents=True)
    (orphan / "project.json").write_text('{"title":"Orphan"}', encoding="utf-8")
    rows = list_projects(tmp_path)
    assert [row.name for row in rows] == ["main", "orphan"]
    assert rows[1].title == "Orphan"


def test_list_projects_skips_missing_and_duplicate_index_rows(tmp_path):
    init_workspace(tmp_path)
    create_project(tmp_path, "main")
    projects_csv_path(tmp_path).write_text(
        "name,title,created_at\n"
        "missing,Missing,today\n"
        "main,Main One,today\n"
        "main,Main Two,today\n",
        encoding="utf-8",
    )
    rows = list_projects(tmp_path)
    assert [row.name for row in rows] == ["main"]
    assert rows[0].title == "Main One"


def test_resolve_project_variants(tmp_path):
    init_workspace(tmp_path)
    create_project(tmp_path, "main")
    assert resolve_project(tmp_path).name == "main"
    assert resolve_project(tmp_path, "main").name == "main"
    with pytest.raises(ProjectError, match="not found"):
        resolve_project(tmp_path, "missing")

    (projects_dir(tmp_path) / "main").rename(projects_dir(tmp_path) / "renamed")
    projects_csv_path(tmp_path).write_text(
        "name,title,created_at\n"
        "renamed,Renamed,today\n",
        encoding="utf-8",
    )
    assert resolve_project(tmp_path).name == "renamed"


def test_resolve_project_requires_name_when_multiple(tmp_path):
    init_workspace(tmp_path)
    create_project(tmp_path, "alpha")
    create_project(tmp_path, "beta")
    with pytest.raises(ProjectError, match="Multiple"):
        resolve_project(tmp_path)


def test_resolve_project_requires_existing_project(tmp_path):
    (tmp_path / ".fdesign" / "projects").mkdir(parents=True)
    projects_csv_path(tmp_path).write_text(
        "name,title,created_at\n",
        encoding="utf-8",
    )
    with pytest.raises(ProjectError, match="No fdesign projects"):
        resolve_project(tmp_path)


def test_load_project_metadata_missing_and_invalid(tmp_path):
    assert load_project_metadata(tmp_path) == {}
    (tmp_path / "project.json").write_text("{bad", encoding="utf-8")
    with pytest.raises(ProjectError, match="Invalid"):
        load_project_metadata(tmp_path)
