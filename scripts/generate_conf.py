#!/usr/bin/env python3
"""Generate rules_for_ru_bypass.conf from template and validate .list files."""

import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

RULE_LINE_RE = re.compile(
    r"^(DOMAIN-SUFFIX|DOMAIN-KEYWORD|DOMAIN|IP-CIDR|URL-REGEX),\s*\S+$"
)


def validate_list_file(path: Path) -> list[str]:
    errors = []
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if not RULE_LINE_RE.match(line):
            errors.append(f"{path.name}:{lineno}: invalid rule: '{line}'")
    return errors


def validate_all_lists(repo_root: Path) -> bool:
    all_errors: list[str] = []
    for list_file in sorted(repo_root.glob("*.list")):
        all_errors.extend(validate_list_file(list_file))
    if all_errors:
        for err in all_errors:
            print(err, file=sys.stderr)
        return False
    return True


def build_header() -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return (
        "# NAME: rules_for_ru_bypass config for Shadowrocket\n"
        "# AUTHOR: RomanAverin\n"
        "# REPO: https://github.com/RomanAverin/shadowrocket-config\n"
        f"# GENERATED: {timestamp}"
    )


def generate_conf(template_path: Path, output_path: Path) -> None:
    content = template_path.read_text(encoding="utf-8")
    content = content.replace("{{GENERATED_HEADER}}", build_header())
    output_path.write_text(content, encoding="utf-8")
    print(f"Wrote {output_path}")


def main() -> int:
    if not validate_all_lists(REPO_ROOT):
        print("Validation failed. Config not generated.", file=sys.stderr)
        return 1
    generate_conf(
        REPO_ROOT / "config" / "conf.template",
        REPO_ROOT / "rules_for_ru_bypass.conf",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
