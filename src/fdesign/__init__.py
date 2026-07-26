"""fdesign — token and component governed prototype toolkit."""

from importlib.metadata import PackageNotFoundError, version as distribution_version
from pathlib import Path
import subprocess


def _git_describe() -> str | None:
    """Return the current source revision when distribution metadata is absent."""
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--always", "--dirty"],
            cwd=Path(__file__).resolve().parents[2],
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip() or None


def get_version() -> str:
    """Return installed build metadata or the current Git tag/revision."""
    try:
        return distribution_version("fdesign")
    except PackageNotFoundError:
        return _git_describe() or "unavailable"


__version__ = get_version()
