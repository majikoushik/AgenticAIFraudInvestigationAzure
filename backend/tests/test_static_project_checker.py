"""
Tests for StaticProjectChecker.
"""
import tempfile
from pathlib import Path

from app.readiness.static_project_checker import StaticProjectChecker


def _checker_for_temp(tmp: Path) -> StaticProjectChecker:
    return StaticProjectChecker(project_root=tmp)


def test_file_exists_true(tmp_path):
    (tmp_path / "test.txt").write_text("hello")
    checker = _checker_for_temp(tmp_path)
    assert checker.file_exists("test.txt") is True


def test_file_exists_false(tmp_path):
    checker = _checker_for_temp(tmp_path)
    assert checker.file_exists("nonexistent.txt") is False


def test_folder_exists_true(tmp_path):
    (tmp_path / "mydir").mkdir()
    checker = _checker_for_temp(tmp_path)
    assert checker.folder_exists("mydir") is True


def test_folder_exists_false(tmp_path):
    checker = _checker_for_temp(tmp_path)
    assert checker.folder_exists("nodir") is False


def test_contains_text_true(tmp_path):
    (tmp_path / "config.py").write_text("SOME_KEY = 'hello world'")
    checker = _checker_for_temp(tmp_path)
    assert checker.contains_text("config.py", "hello world") is True


def test_contains_text_false(tmp_path):
    (tmp_path / "config.py").write_text("SOME_KEY = 'hello world'")
    checker = _checker_for_temp(tmp_path)
    assert checker.contains_text("config.py", "missing text") is False


def test_contains_text_missing_file(tmp_path):
    checker = _checker_for_temp(tmp_path)
    assert checker.contains_text("missing.py", "anything") is False


def test_scan_clean_files(tmp_path):
    (tmp_path / "safe.py").write_text("x = 1")
    checker = _checker_for_temp(tmp_path)
    result = checker.scan_for_secret_patterns(["safe.py"])
    assert result["clean"] is True
    assert result["total_files_scanned"] == 1


def test_scan_detects_placeholder_env(tmp_path):
    """Placeholder values (empty, angle-bracket) should NOT be flagged."""
    (tmp_path / ".env.example").write_text("AZURE_OPENAI_API_KEY=\npassword=<your-password-here>")
    checker = _checker_for_temp(tmp_path)
    # The checker skips .env.example by its skip pattern; result should show 0 files
    result = checker.scan_for_secret_patterns([".env.example"])
    # file skipped OR no findings
    assert result["clean"] is True or result["findings"] == []


def test_check_docs_exist_false(tmp_path):
    checker = _checker_for_temp(tmp_path)
    assert checker.check_docs_exist("architecture") is False


def test_check_docs_exist_true(tmp_path):
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "architecture-overview.md").write_text("# Architecture")
    checker = _checker_for_temp(tmp_path)
    assert checker.check_docs_exist("architecture") is True


def test_check_bicep_module_exists_false(tmp_path):
    checker = _checker_for_temp(tmp_path)
    assert checker.check_bicep_module_exists("key-vault") is False


def test_check_tests_exist_false(tmp_path):
    checker = _checker_for_temp(tmp_path)
    assert checker.check_tests_exist("*agent*") is False
