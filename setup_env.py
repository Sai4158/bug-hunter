"""Create a project-local Python environment; never download an AI model automatically."""
import argparse
import subprocess
import sys
import venv
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def dependencies_ready():
    """Check the current interpreter without installing or contacting the network."""
    try:
        for line in (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines():
            if line.strip() and not line.startswith("#"):
                name, required = line.strip().split("==", 1)
                if version(name) != required:
                    return False
        return True
    except (OSError, ValueError, PackageNotFoundError):
        return False


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true", help="Launch Bug Hunter after setup.")
    parser.add_argument("--check", action="store_true", help="Check pinned dependencies in the current Python only.")
    args = parser.parse_args(argv)
    if sys.version_info < (3, 11):
        print("Install Python 3.11 or newer, then run setup again.")
        return 1
    if args.check:
        return 0 if dependencies_ready() else 1
    environment = ROOT / ".venv"
    python = environment / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
    try:
        if environment.exists() and not python.is_file():
            print("The existing .venv is incomplete. Rename it as a backup, then retry setup.")
            return 1
        if not python.is_file():
            print("Creating .venv in the project folder...")
            venv.EnvBuilder(with_pip=True).create(environment)
        subprocess.run([str(python), "-c", "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)"],
                       cwd=ROOT, shell=False, check=True)
        print("Installing project dependencies into .venv...")
        subprocess.run([str(python), "-m", "pip", "install", "--disable-pip-version-check",
                        "-r", str(ROOT / "requirements.txt")], cwd=ROOT, shell=False, check=True)
        subprocess.run([str(python), "-m", "pip", "check"], cwd=ROOT, shell=False, check=True)
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"Setup did not complete: {exc}")
        print("Check your Python version, internet access, and the installer output above.")
        return 1
    print("Setup complete. AI models are separate: see README.md for Ollama setup.")
    if args.run:
        return subprocess.run([str(python), str(ROOT / "launch.py")],
                              cwd=ROOT, shell=False, check=False).returncode
    print("Start with start.bat (Windows) or bash start.sh (macOS/Linux).")
    print("Use run.bat / bash run.sh for a foreground launch without guided Ollama setup.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
