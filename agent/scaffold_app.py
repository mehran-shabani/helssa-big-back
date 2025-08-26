#!/usr/bin/env python3
import argparse
import os
import shutil
from pathlib import Path
from datetime import datetime

TEMPLATES_DIR = Path(__file__).parent / "TEMPLATES"
CODE_TEMPLATES = TEMPLATES_DIR / "code"
DOC_TEMPLATES = {
    "plan": TEMPLATES_DIR / "PLAN.md.template",
    "readme": TEMPLATES_DIR / "README.md.template",
    "checklist": TEMPLATES_DIR / "CHECKLIST.json.template",
    "progress": TEMPLATES_DIR / "PROGRESS.json.template",
    "log": TEMPLATES_DIR / "LOG.md.template",
}

PLACEHOLDERS_DEFAULTS = {
    "APP_NAME": None,
    "APP_CLASS_NAME": None,
    "APP_VERBOSE_NAME": None,
    "APP_DESCRIPTION": "توضیح کوتاه اپ",
    "APP_OVERVIEW": "نمای کلی اپ",
    "PATIENT_FEATURES_LIST": "- ویژگی نمونه برای بیمار",
    "DOCTOR_FEATURES_LIST": "- ویژگی نمونه برای پزشک",
    "SHARED_FEATURES_LIST": "- ویژگی نمونه مشترک",
    "URL_PREFIX": None,
    "CREATION_DATE": None,
}


def render_template_text(text: str, context: dict) -> str:
    for key, value in context.items():
        placeholder = "{{" + key + "}}"
        text = text.replace(placeholder, value if value is not None else "")
    return text


def copy_and_render(src: Path, dst: Path, context: dict, skip_existing: bool = False):
    if skip_existing and dst.exists():
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.is_dir():
        shutil.copytree(src, dst, dirs_exist_ok=True)
        return
    content = src.read_text(encoding="utf-8")
    rendered = render_template_text(content, context)
    dst.write_text(rendered, encoding="utf-8")


def scaffold(app_name: str, app_verbose: str | None = None, url_prefix: str | None = None, *, code_only: bool = False, skip_existing: bool = False):
    apps_root = Path(__file__).parent / "apps"
    app_dir = apps_root / app_name
    app_dir.mkdir(parents=True, exist_ok=True)

    class_name = ''.join(part.capitalize() for part in app_name.split('_')) + "Config"
    context = dict(PLACEHOLDERS_DEFAULTS)
    context.update({
        "APP_NAME": app_name,
        "APP_CLASS_NAME": class_name,
        "APP_VERBOSE_NAME": app_verbose or app_name.replace('_', ' ').title(),
        "URL_PREFIX": url_prefix or app_name.replace('_', '-') ,
        "CREATION_DATE": datetime.utcnow().isoformat() + "Z",
    })

    if not code_only:
        # Docs
        copy_and_render(DOC_TEMPLATES["plan"], app_dir / "PLAN.md", context, skip_existing=skip_existing)
        copy_and_render(DOC_TEMPLATES["readme"], app_dir / "README.md", context, skip_existing=skip_existing)
        copy_and_render(DOC_TEMPLATES["checklist"], app_dir / "CHECKLIST.json", context, skip_existing=skip_existing)
        copy_and_render(DOC_TEMPLATES["progress"], app_dir / "PROGRESS.json", context, skip_existing=skip_existing)
        copy_and_render(DOC_TEMPLATES["log"], app_dir / "LOG.md", context, skip_existing=skip_existing)

        # Charts dir
        (app_dir / "charts").mkdir(exist_ok=True)

    # Code
    app_code = app_dir / "app_code"
    app_code.mkdir(exist_ok=True)
    copy_and_render(CODE_TEMPLATES / "app_code" / "__init__.py.template", app_code / "__init__.py", context, skip_existing=skip_existing)
    copy_and_render(CODE_TEMPLATES / "app_code" / "apps.py.template", app_code / "apps.py", context, skip_existing=skip_existing)
    copy_and_render(CODE_TEMPLATES / "app_code" / "models.py.template", app_code / "models.py", context, skip_existing=skip_existing)
    copy_and_render(CODE_TEMPLATES / "app_code" / "admin.py.template", app_code / "admin.py", context, skip_existing=skip_existing)
    copy_and_render(CODE_TEMPLATES / "app_code" / "serializers.py.template", app_code / "serializers.py", context, skip_existing=skip_existing)
    copy_and_render(CODE_TEMPLATES / "app_code" / "views.py.template", app_code / "views.py", context, skip_existing=skip_existing)
    copy_and_render(CODE_TEMPLATES / "app_code" / "urls.py.template", app_code / "urls.py", context, skip_existing=skip_existing)
    copy_and_render(CODE_TEMPLATES / "app_code" / "permissions.py.template", app_code / "permissions.py", context, skip_existing=skip_existing)
    copy_and_render(CODE_TEMPLATES / "app_code" / "forms.py.template", app_code / "forms.py", context, skip_existing=skip_existing)

    # Cores
    cores_dir = app_code / "cores"
    cores_dir.mkdir(exist_ok=True)
    copy_and_render(CODE_TEMPLATES / "app_code" / "cores" / "__init__.py.template", cores_dir / "__init__.py", context, skip_existing=skip_existing)
    copy_and_render(CODE_TEMPLATES / "app_code" / "cores" / "api_ingress.py.template", cores_dir / "api_ingress.py", context, skip_existing=skip_existing)
    copy_and_render(CODE_TEMPLATES / "app_code" / "cores" / "text_processor.py.template", cores_dir / "text_processor.py", context, skip_existing=skip_existing)
    copy_and_render(CODE_TEMPLATES / "app_code" / "cores" / "speech_processor.py.template", cores_dir / "speech_processor.py", context, skip_existing=skip_existing)
    copy_and_render(CODE_TEMPLATES / "app_code" / "cores" / "orchestrator.py.template", cores_dir / "orchestrator.py", context, skip_existing=skip_existing)

    # Migrations
    migrations_dir = app_code / "migrations"
    migrations_dir.mkdir(exist_ok=True)
    copy_and_render(CODE_TEMPLATES / "app_code" / "migrations" / "__init__.py.template", migrations_dir / "__init__.py", context, skip_existing=skip_existing)

    # Tests
    tests_dir = app_code / "tests"
    tests_dir.mkdir(exist_ok=True)
    copy_and_render(CODE_TEMPLATES / "app_code" / "tests" / "__init__.py.template", tests_dir / "__init__.py", context, skip_existing=skip_existing)
    copy_and_render(CODE_TEMPLATES / "app_code" / "tests" / "test_models.py.template", tests_dir / "test_models.py", context, skip_existing=skip_existing)
    copy_and_render(CODE_TEMPLATES / "app_code" / "tests" / "test_views.py.template", tests_dir / "test_views.py", context, skip_existing=skip_existing)
    copy_and_render(CODE_TEMPLATES / "app_code" / "tests" / "test_serializers.py.template", tests_dir / "test_serializers.py", context, skip_existing=skip_existing)
    copy_and_render(CODE_TEMPLATES / "app_code" / "tests" / "test_integration.py.template", tests_dir / "test_integration.py", context, skip_existing=skip_existing)

    print(f"✅ Scaffolded app at {app_dir}")


def main():
    parser = argparse.ArgumentParser(description="Scaffold a new HELSSA agent app under agent/apps")
    parser.add_argument("app_name", help="snake_case app name, e.g., patient_chatbot")
    parser.add_argument("--verbose-name", dest="app_verbose", default=None, help="Human readable app name")
    parser.add_argument("--url-prefix", dest="url_prefix", default=None, help="URL prefix for including urls")
    parser.add_argument("--code-only", dest="code_only", action="store_true", help="Only scaffold code skeleton, skip docs")
    parser.add_argument("--skip-existing", dest="skip_existing", action="store_true", help="Do not overwrite existing files")
    args = parser.parse_args()

    scaffold(args.app_name, args.app_verbose, args.url_prefix, code_only=args.code_only, skip_existing=args.skip_existing)


if __name__ == "__main__":
    main()