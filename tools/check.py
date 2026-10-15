"""One-command check: unit tests + text lint. Exit code gates commits (pre-commit hook)."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    r = subprocess.run([sys.executable, "-X", "utf8", "-m", "pytest", "-q", "-x", str(ROOT / "tests")], cwd=ROOT)
    lint = subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "tools" / "lint.py")], cwd=ROOT)
    return r.returncode or lint.returncode


if __name__ == "__main__":
    sys.exit(main())
