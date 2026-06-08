from pathlib import Path


def test_no_secret_scan_script_exists() -> None:
    assert Path("scripts/security/check-no-secrets.ps1").exists()
    assert Path("scripts/security/check-no-secrets.sh").exists()
