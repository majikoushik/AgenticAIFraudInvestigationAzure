import subprocess
import sys
from pathlib import Path


def test_security_report_script_generates_report() -> None:
    result = subprocess.run([sys.executable, "scripts/security/generate-security-report.py"], check=True, capture_output=True, text=True)
    report_path = Path(result.stdout.strip())
    assert report_path.exists()
    assert "Key Vault module" in report_path.read_text(encoding="utf-8")
