#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).parent
APPS_DIR = ROOT / "apps"


def build_tree(dir_path: Path, prefix: str = "") -> list[str]:
    lines: list[str] = []
    entries = sorted(dir_path.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
    for i, entry in enumerate(entries):
        connector = "└── " if i == len(entries) - 1 else "├── "
        lines.append(f"{prefix}{connector}{entry.name}")
        if entry.is_dir():
            extension = "    " if i == len(entries) - 1 else "│   "
            lines.extend(build_tree(entry, prefix + extension))
    return lines


def extract_api_endpoints(plan_md: str) -> list[str]:
    endpoints: list[str] = []
    # Look for code fences under headings mentioning API or Endpoints
    code_blocks = re.findall(r"```[\s\S]*?```", plan_md)
    for block in code_blocks:
        for line in block.strip('`').splitlines():
            if re.match(r"^(GET|POST|PUT|PATCH|DELETE)\s+/", line.strip(), re.IGNORECASE):
                endpoints.append(line.strip())
    return endpoints


def main():
    # Generate project tree
    tree_lines: list[str] = ["agent/", "├── apps/"]
    for app_dir in sorted((APPS_DIR.iterdir() if APPS_DIR.exists() else []), key=lambda p: p.name.lower()):
        tree_lines.append(f"│   ├── {app_dir.name}/")
        for sub in ["PLAN.md", "CHECKLIST.json", "PROGRESS.json", "LOG.md", "README.md", "charts/"]:
            tree_lines.append(f"│   │   ├── {sub}")
    (ROOT / "PROJECT_TREE.md").write_text("\n".join(tree_lines), encoding="utf-8")

    # Generate APIs inventory
    apis_lines: list[str] = ["# Unified API Inventory\n"]
    for app_dir in sorted((APPS_DIR.iterdir() if APPS_DIR.exists() else []), key=lambda p: p.name.lower()):
        plan_path = app_dir / "PLAN.md"
        apis_lines.append(f"## {app_dir.name}")
        if plan_path.exists():
            plan_text = plan_path.read_text(encoding="utf-8")
            endpoints = extract_api_endpoints(plan_text)
            if endpoints:
                apis_lines.extend([f"- {e}" for e in endpoints])
            else:
                apis_lines.append("- (No explicit endpoints listed)")
        else:
            apis_lines.append("- (Missing PLAN.md)")
        apis_lines.append("")
    (ROOT / "APIS.md").write_text("\n".join(apis_lines), encoding="utf-8")

    print("✅ Generated PROJECT_TREE.md and APIS.md")


if __name__ == "__main__":
    main()