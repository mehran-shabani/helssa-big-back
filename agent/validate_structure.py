#!/usr/bin/env python3
from pathlib import Path
import json

ROOT = Path(__file__).parent
APPS_DIR = ROOT / "apps"

REQUIRED_TOP = [
    "PLAN.md",
    "CHECKLIST.json",
    "PROGRESS.json",
    "LOG.md",
    "README.md",
    "charts",
    "app_code",
]

REQUIRED_CODE = [
    "__init__.py",
    "apps.py",
    "models.py",
    "admin.py",
    "serializers.py",
    "views.py",
    "urls.py",
    "permissions.py",
    "forms.py",
    "cores",
    "migrations",
    "tests",
]


def validate_app(app_dir: Path) -> list[str]:
    errors: list[str] = []

    # Required top-level items
    for req in REQUIRED_TOP:
        if not (app_dir / req).exists():
            errors.append(f"Missing {req}")

    # Charts subdir present
    if (app_dir / "charts").exists() and not (app_dir / "charts").is_dir():
        errors.append("charts exists but is not a directory")

    # app_code structure
    code_dir = app_dir / "app_code"
    if code_dir.exists():
        for req in REQUIRED_CODE:
            if not (code_dir / req).exists():
                errors.append(f"Missing app_code/{req}")
    else:
        errors.append("Missing app_code/")

    # JSON validity
    for json_file in ["CHECKLIST.json", "PROGRESS.json"]:
        jf = app_dir / json_file
        if jf.exists():
            try:
                json.loads(jf.read_text(encoding="utf-8"))
            except Exception as exc:
                errors.append(f"Invalid {json_file}: {exc}")
        else:
            errors.append(f"Missing {json_file}")

    return errors


def main():
    any_errors = False
    for app_dir in sorted((APPS_DIR.iterdir() if APPS_DIR.exists() else []), key=lambda p: p.name.lower()):
        if not app_dir.is_dir():
            continue
        errs = validate_app(app_dir)
        if errs:
            any_errors = True
            print(f"❌ {app_dir.name}")
            for e in errs:
                print(f"  - {e}")
        else:
            print(f"✅ {app_dir.name} structure OK")
    if any_errors:
        exit(1)


if __name__ == "__main__":
    main()