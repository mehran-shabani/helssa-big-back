#!/usr/bin/env python3
import argparse
import json
import os
import sys
import traceback
from typing import Dict, Any, List


class Issue:
    def __init__(self, id: str, title: str, severity: str, file: str = None, lines: List[int] = None, details: Dict[str, Any] = None):
        self.id = id
        self.title = title
        self.severity = severity
        self.file = file
        self.lines = lines or []
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "severity": self.severity,
            "file": self.file,
            "lines": self.lines,
            "details": self.details,
        }


def agent_scan_settings(base_dir: str) -> List[Issue]:
    issues: List[Issue] = []
    settings_path = os.path.join(base_dir, "helssa", "settings.py")
    if not os.path.exists(settings_path):
        issues.append(Issue(
            id="settings_missing",
            title="helssa/settings.py not found",
            severity="critical",
            file=settings_path,
        ))
        return issues

    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        issues.append(Issue(
            id="settings_read_error",
            title=f"Cannot read settings.py: {e}",
            severity="critical",
            file=settings_path,
        ))
        return issues

    # Duplicated AUTH_USER_MODEL definitions
    auth_lines = [i for i, line in enumerate(content.splitlines(), start=1) if "AUTH_USER_MODEL" in line]
    if len(auth_lines) > 1:
        issues.append(Issue(
            id="auth_user_model_duplicate",
            title="Multiple AUTH_USER_MODEL definitions in settings.py",
            severity="high",
            file=settings_path,
            lines=auth_lines,
        ))

    # REST_FRAMEWORK duplicated blocks or malformed dict (quick heuristic)
    if content.count("REST_FRAMEWORK =") > 1:
        issues.append(Issue(
            id="rest_framework_duplicate",
            title="Multiple REST_FRAMEWORK settings blocks",
            severity="medium",
            file=settings_path,
        ))

    # SIMPLE_JWT presence
    if "SIMPLE_JWT =" not in content:
        issues.append(Issue(
            id="simple_jwt_missing",
            title="SIMPLE_JWT settings missing",
            severity="low",
            file=settings_path,
        ))

    # INSTALLED_APPS sanity
    if "rest_framework" not in content:
        issues.append(Issue(
            id="drf_missing",
            title="rest_framework not in INSTALLED_APPS",
            severity="critical",
            file=settings_path,
        ))

    return issues


def agent_scan_urls(base_dir: str) -> List[Issue]:
    issues: List[Issue] = []
    urls_path = os.path.join(base_dir, "helssa", "urls.py")
    if not os.path.exists(urls_path):
        issues.append(Issue(
            id="urls_missing",
            title="helssa/urls.py not found",
            severity="critical",
            file=urls_path,
        ))
        return issues
    try:
        with open(urls_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        issues.append(Issue(
            id="urls_read_error",
            title=f"Cannot read urls.py: {e}",
            severity="critical",
            file=urls_path,
        ))
        return issues

    # Heuristic: detect missing commas in dictionaries
    if "available_services" in content and "'auth_otp': '/api/auth/'\n            'adminportal':" in content:
        issues.append(Issue(
            id="urls_missing_comma",
            title="Missing comma in available_services dict",
            severity="high",
            file=urls_path,
        ))

    # Missing imports like settings/static
    needs_static = ("static(" in content) and ("from django.conf import settings" not in content or "from django.conf.urls.static import static" not in content)
    if needs_static:
        issues.append(Issue(
            id="urls_missing_static_imports",
            title="urls.py uses static but missing imports",
            severity="high",
            file=urls_path,
        ))

    return issues


def agent_scan_requirements(base_dir: str) -> List[Issue]:
    path = os.path.join(base_dir, "requirements.txt")
    issues: List[Issue] = []
    if not os.path.exists(path):
        return issues
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        issues.append(Issue("requirements_read_error", f"Cannot read requirements.txt: {e}", "low", file=path))
        return issues
    if "drf-spectacular" not in content:
        issues.append(Issue("drf_spectacular_missing", "drf-spectacular not listed in requirements.txt", "medium", file=path))
    return issues


def aggregate_issues(all_issues: List[Issue]) -> Dict[str, Any]:
    by_severity: Dict[str, List[Dict[str, Any]]] = {}
    for issue in all_issues:
        by_severity.setdefault(issue.severity, []).append(issue.to_dict())
    return {
        "total": len(all_issues),
        "by_severity": {k: sorted(v, key=lambda d: (d.get("file") or "", d.get("id"))) for k, v in by_severity.items()},
        "issues": [i.to_dict() for i in all_issues],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run debug orchestration agents")
    parser.add_argument("--base", default=os.getcwd(), help="Project base directory")
    parser.add_argument("--json", action="store_true", help="Output JSON report to stdout")
    parser.add_argument("--out", default=os.path.join("debug_orchestration", "reports", "report.json"), help="Path to write JSON report")
    args = parser.parse_args()

    base_dir = args.base
    all_issues: List[Issue] = []
    try:
        all_issues.extend(agent_scan_settings(base_dir))
        all_issues.extend(agent_scan_urls(base_dir))
        all_issues.extend(agent_scan_requirements(base_dir))
    except Exception:
        all_issues.append(Issue("runner_exception", traceback.format_exc(), "critical"))

    report = aggregate_issues(all_issues)

    os.makedirs(os.path.join(base_dir, "debug_orchestration", "reports"), exist_ok=True)
    with open(os.path.join(base_dir, args.out), "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())

