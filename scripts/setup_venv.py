#!/usr/bin/env python3
"""
Create a local virtual environment at ./.venv and install project dependencies.

Usage:
  python scripts/setup_venv.py
  # or (after making executable)
  ./scripts/setup_venv.py
"""

from __future__ import annotations

import platform
import subprocess
import sys
from pathlib import Path
import shutil


def get_project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def get_venv_python_path(venv_dir: Path) -> Path:
    if platform.system() == "Windows":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def run(cmd: list[str], cwd: Path | None = None) -> None:
    completed = subprocess.run(cmd, cwd=str(cwd) if cwd else None)
    if completed.returncode != 0:
        raise SystemExit(f"Command failed ({completed.returncode}): {' '.join(cmd)}")


def find_python310_command() -> str | None:
    if platform.system() == "Windows":
        # Try the launcher first
        py_launcher = shutil.which("py")
        if py_launcher:
            return "py -3.10"
        # Fallback to python3.10 if available
        if shutil.which("python3.10"):
            return "python3.10"
        if shutil.which("python"):
            # Check if it's 3.10
            try:
                out = subprocess.check_output(["python", "-c", "import sys; print('.'.join(map(str, sys.version_info[:2])))"]).decode().strip()
                if out == "3.10":
                    return "python"
            except Exception:
                pass
        return None
    # Unix-like
    if shutil.which("python3.10"):
        return "python3.10"
    if shutil.which("python3"):
        try:
            out = subprocess.check_output(["python3", "-c", "import sys; print('.'.join(map(str, sys.version_info[:2])))"]).decode().strip()
            if out == "3.10":
                return "python3"
        except Exception:
            pass
    return None


def ensure_venv(venv_dir: Path) -> Path:
    desired_cmd = find_python310_command()
    if not desired_cmd:
        raise SystemExit(
            "Python 3.10 not found. Please install Python 3.10 (e.g., via pyenv) and retry."
        )

    def create_with_310() -> None:
        print(f"Creating virtual environment with Python 3.10 at: {venv_dir}")
        # desired_cmd may contain a space (py -3.10), so use shell when needed
        if " " in desired_cmd:
            run(["bash", "-lc", f"{desired_cmd} -m venv '{venv_dir}'"])  # safe on Unix
        else:
            run([desired_cmd, "-m", "venv", str(venv_dir)])

    if not venv_dir.exists():
        create_with_310()
    else:
        print(f"Virtual environment already exists: {venv_dir}")

    venv_python = get_venv_python_path(venv_dir)
    if not venv_python.exists():
        raise SystemExit(
            f"Could not find venv python at expected path: {venv_python}\n"
            f"Try removing {venv_dir} and re-running this script."
        )

    # Verify Python version is 3.10; if not, recreate with 3.10
    try:
        version = subprocess.check_output([str(venv_python), "-c", "import sys; print('.'.join(map(str, sys.version_info[:2])))"]).decode().strip()
    except Exception:
        version = ""
    if version != "3.10":
        print(f"Existing venv uses Python {version or 'unknown'}, recreating with Python 3.10...")
        # Remove and recreate
        import shutil as _sh
        _sh.rmtree(venv_dir, ignore_errors=True)
        create_with_310()
        venv_python = get_venv_python_path(venv_dir)
        if not venv_python.exists():
            raise SystemExit(f"Failed to create venv with Python 3.10 at {venv_dir}")
    return venv_python


def upgrade_pip(venv_python: Path) -> None:
    print("Upgrading pip, setuptools, and wheel...")
    run([str(venv_python), "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"])


def install_requirements(venv_python: Path, project_root: Path) -> None:
    requirements = project_root / "src" / "backend" / "requirements.txt"
    if requirements.exists():
        print(f"Installing dependencies from {requirements}...")
        run([str(venv_python), "-m", "pip", "install", "-r", str(requirements)])
    else:
        print("No requirements.txt found. Skipping dependency installation.")


def main() -> None:
    project_root = get_project_root()
    venv_dir = project_root / ".venv"

    venv_python = ensure_venv(venv_dir)
    upgrade_pip(venv_python)
    install_requirements(venv_python, project_root)

    # Post-run guidance
    if platform.system() == "Windows":
        activate_hint = ".venv\\Scripts\\activate"
    else:
        activate_hint = "source .venv/bin/activate"

    print("\nDone. Virtual environment is ready.")
    print(f"Activate it with: {activate_hint}")
    print("Then run your scripts with the venv's Python.")


if __name__ == "__main__":
    main()


