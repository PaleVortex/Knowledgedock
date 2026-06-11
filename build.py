#!/usr/bin/env python
"""
Knowledgedock build & test utility.
Usage: python build.py [command]

Commands:
  test              Run pytest on backend
  test-verbose      Run pytest with verbose output
  test-coverage     Run tests and generate coverage report
  lint              Run flake8 code linting
  format            Format code with black & isort
  check             Run all checks (lint + type + test)
  build             Build executable with PyInstaller
  run               Run the app directly
  run-backend       Run just the backend server
  clean             Remove build artifacts
  help              Show this message
"""

import sys
import subprocess
import shutil
import shlex
import os
from pathlib import Path


def run_command(cmd, description):
    """Run a command and report results."""
    print(f"\n{'=' * 60}")
    print(f"  {description}")
    print(f"{'=' * 60}\n")
    # Use shlex for proper command parsing
    if isinstance(cmd, str):
        cmd_parts = shlex.split(cmd)
    else:
        cmd_parts = cmd
    
    # Replace 'python' with current Python executable for venv compatibility
    if cmd_parts[0] == 'python':
        cmd_parts[0] = sys.executable
    
    result = subprocess.run(cmd_parts)
    if result.returncode != 0:
        print(f"\n[FAILED] {description} FAILED")
        sys.exit(1)
    print(f"\n[OK] {description} succeeded")


def test():
    """Run pytest backend tests."""
    run_command("python -m pytest backend_tests.py -v --tb=short", "Running Tests")


def test_verbose():
    """Run pytest with verbose output."""
    run_command("python -m pytest backend_tests.py -vv --tb=long", "Running Tests (Verbose)")


def test_coverage():
    """Run tests with coverage report."""
    run_command(
        "python -m pytest backend_tests.py -v --cov=backend --cov-report=html --cov-report=term",
        "Running Tests with Coverage"
    )
    print("\n[OK] Coverage report generated: htmlcov/index.html")


def lint():
    """Run flake8 linting."""
    run_command(
        "python -m flake8 . --count --select=E9,F63,F7,F82 --statistics --exclude=.git,__pycache__,build,dist",
        "Linting Code (Critical)"
    )
    run_command(
        "python -m flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --exclude=.git,__pycache__,build,dist",
        "Linting Code (Warnings)"
    )


def format_code():
    """Format code with black & isort."""
    run_command("python -m black . --exclude=build,dist", "Formatting with black")
    run_command("python -m isort . --skip-glob=build,dist", "Organizing imports with isort")


def check():
    """Run all checks."""
    print("\nRunning all checks...\n")
    try:
        lint()
        test()
        print("\n" + "=" * 60)
        print("  [OK] All checks passed!")
        print("=" * 60)
    except SystemExit:
        print("\n" + "=" * 60)
        print("  [FAILED] Some checks failed")
        print("=" * 60)
        sys.exit(1)


def build():
    """Build executable with PyInstaller."""
    assets_dir = Path("assets")
    if not assets_dir.exists():
        print(f"\n[WARNING] Assets directory not found at {assets_dir}")
        print("Continuing without asset bundling...")
        cmd = 'pyinstaller --onefile --windowed --name Knowledgedock main.py'
    else:
        icon = assets_dir / "app_icon.ico" if (assets_dir / "app_icon.ico").exists() else ""
        icon_param = f'--icon={icon}' if icon else ""
        cmd = f'pyinstaller --onefile --windowed --name Knowledgedock --add-data "assets:assets" {icon_param} main.py'
    
    run_command(cmd, "Building Executable")
    exe_path = Path("dist") / "Knowledgedock.exe"
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"\n[OK] Executable created: {exe_path} ({size_mb:.1f} MB)")


def run_app():
    """Run the application."""
    run_command("python main.py", "Running Knowledgedock")


def run_backend_only():
    """Run just the backend server."""
    run_command("python backend.py", "Running Backend Server")


def clean():
    """Remove build artifacts."""
    dirs_to_remove = ["build", "dist", "__pycache__", ".pytest_cache", ".coverage", "htmlcov", "*.egg-info"]
    for pattern in dirs_to_remove:
        for path in Path(".").glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"Removed {path}")
            elif path.is_file():
                path.unlink()
                print(f"Removed {path}")
    print("[OK] Cleanup complete")


def show_help():
    """Display help message."""
    print(__doc__)


# Command mapping
commands = {
    'test': test,
    'test-verbose': test_verbose,
    'test-coverage': test_coverage,
    'lint': lint,
    'format': format_code,
    'check': check,
    'build': build,
    'run': run_app,
    'run-backend': run_backend_only,
    'clean': clean,
    'help': show_help,
}


if __name__ == '__main__':
    os.chdir(Path(__file__).parent)  # Ensure we're in the right directory
    
    if len(sys.argv) < 2:
        show_help()
        sys.exit(0)
    
    command = sys.argv[1].lower()
    
    if command not in commands:
        print(f"[ERROR] Unknown command: {command}\n")
        show_help()
        sys.exit(1)
    
    try:
        commands[command]()
    except KeyboardInterrupt:
        print("\n\n[CANCELLED] Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        sys.exit(1)
