"""
Static Project Checker.
Performs file, folder, text, and secret-pattern checks against the local project.

SECURITY NOTE: Secret scan reports file path and pattern type ONLY.
It NEVER returns, logs, or stores the actual suspected secret value.
"""
from __future__ import annotations

import fnmatch
import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)

# Root of the project (4 levels up from this file: readiness/ -> app/ -> backend/ -> project/)
_PROJECT_ROOT: Path = Path(__file__).resolve().parents[4]

# Secret patterns to detect — matched against file content
# Pattern: (label, regex)
_SECRET_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("api_key_assignment", re.compile(r"(?i)api[_-]?key\s*=\s*['\"][A-Za-z0-9/+_\-]{8,}", re.MULTILINE)),
    ("password_assignment", re.compile(r"(?i)password\s*=\s*['\"][^'\"]{4,}", re.MULTILINE)),
    ("connection_string", re.compile(r"(?i)connection[_-]?string\s*=\s*['\"][^'\"]{8,}", re.MULTILINE)),
    ("account_key", re.compile(r"AccountKey=[A-Za-z0-9+/=]{20,}", re.MULTILINE)),
    ("bearer_token", re.compile(r"Bearer\s+eyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+", re.MULTILINE)),
    ("teams_webhook", re.compile(r"webhook\.office\.com/webhookb2/", re.MULTILINE)),
    ("instrumentation_key", re.compile(r"(?i)instrumentationkey\s*=\s*[0-9a-f\-]{32,}", re.MULTILINE)),
    ("openai_sk_key", re.compile(r"AZURE_OPENAI_API_KEY\s*=\s*sk-[A-Za-z0-9\-]{20,}", re.MULTILINE)),
    ("storage_endpoint", re.compile(r"DefaultEndpointsProtocol=https;AccountName=[^;]+;AccountKey=[A-Za-z0-9+/=]{10,}", re.MULTILINE)),
]

# Files/folders to always skip during secret scanning
_SCAN_SKIP_PATTERNS = [
    ".git",
    "__pycache__",
    "node_modules",
    ".next",
    "*.pyc",
    "*.pyo",
    "package-lock.json",
    ".env.example",   # Placeholders with empty values are expected
]


def _should_skip(path: Path) -> bool:
    for pattern in _SCAN_SKIP_PATTERNS:
        if fnmatch.fnmatch(path.name, pattern):
            return True
    for part in path.parts:
        if part in {".git", "__pycache__", "node_modules", ".next"}:
            return True
    return False


def _is_placeholder_value(line: str) -> bool:
    """
    Return True if the matched line appears to be an empty/placeholder env var.
    e.g.  API_KEY=  or  api_key=""  or  api_key=<your-key-here>
    """
    # Empty value after = or just whitespace / angle-bracket placeholder
    placeholder_re = re.compile(r"""[=:]\s*(?:"|')?(?:<[^>]+>|\$\{[^}]+\}|YOUR[_-]?[A-Z]+|PLACEHOLDER|CHANGEME)?\s*(?:"|')?\s*$""", re.IGNORECASE)
    return bool(placeholder_re.search(line))


class StaticProjectChecker:
    """Performs static file-system checks for the production readiness assessment."""

    def __init__(self, project_root: Path | None = None) -> None:
        self.project_root = project_root or _PROJECT_ROOT

    def file_exists(self, relative_path: str) -> bool:
        """Check if a file exists relative to the project root."""
        return (self.project_root / relative_path).is_file()

    def folder_exists(self, relative_path: str) -> bool:
        """Check if a folder exists relative to the project root."""
        return (self.project_root / relative_path).is_dir()

    def contains_text(self, relative_path: str, text: str) -> bool:
        """Check if a file contains the given text substring."""
        path = self.project_root / relative_path
        if not path.is_file():
            return False
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
            return text in content
        except Exception:
            return False

    def check_bicep_module_exists(self, module_name: str) -> bool:
        """Check if a Bicep file with the given name (or containing the module name) exists."""
        bicep_dir = self.project_root / "infra" / "bicep"
        if not bicep_dir.is_dir():
            return False
        for f in bicep_dir.rglob("*.bicep"):
            if module_name.lower() in f.name.lower():
                return True
        return False

    def check_docs_exist(self, doc_name_fragment: str) -> bool:
        """Check if any .md file in docs/ matches the fragment."""
        docs_dir = self.project_root / "docs"
        if not docs_dir.is_dir():
            return False
        fragment = doc_name_fragment.lower()
        for f in docs_dir.rglob("*.md"):
            if fragment in f.name.lower():
                return True
        return False

    def check_tests_exist(self, pattern: str) -> bool:
        """Check if any test file matching the glob pattern exists under backend/tests/."""
        tests_dir = self.project_root / "backend" / "tests"
        if not tests_dir.is_dir():
            return False
        return any(tests_dir.rglob(pattern))

    def scan_for_secret_patterns(self, relative_paths: list[str]) -> dict:
        """
        Scan the given paths (files or directories) for likely secret patterns.

        Returns a dict with:
          - total_files_scanned: int
          - findings: list of {file, pattern_type} — NEVER includes the matched value
          - clean: bool (True if no findings)
        """
        findings: list[dict] = []
        total_scanned = 0

        for rel_path in relative_paths:
            full_path = self.project_root / rel_path
            if full_path.is_file():
                files = [full_path]
            elif full_path.is_dir():
                files = [f for f in full_path.rglob("*") if f.is_file()]
            else:
                continue

            for file_path in files:
                if _should_skip(file_path):
                    continue
                try:
                    content = file_path.read_text(encoding="utf-8", errors="replace")
                    total_scanned += 1
                    for label, pattern in _SECRET_PATTERNS:
                        for match in pattern.finditer(content):
                            # Extract only the line, not the matched secret value
                            line = content[content.rfind("\n", 0, match.start()) + 1: content.find("\n", match.end())]
                            if _is_placeholder_value(line):
                                # Skip placeholder values in .env.example style files
                                continue
                            relative = str(file_path.relative_to(self.project_root)).replace("\\", "/")
                            findings.append({
                                "file": relative,
                                "pattern_type": label,
                                # SECURITY: never include the matched value
                            })
                except Exception:
                    logger.debug("Could not scan file %s", file_path)

        return {
            "total_files_scanned": total_scanned,
            "findings": findings,
            "clean": len(findings) == 0,
        }


# Singleton instance
static_checker = StaticProjectChecker()
