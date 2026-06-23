import os
import shutil
import tempfile
import sys
import pytest
from pathlib import Path

# Ensure the backend directory is in the PYTHONPATH so tests can run from anywhere
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.config import settings

@pytest.fixture(scope="session", autouse=True)
def isolate_synthetic_data():
    """
    Ensure tests do not mutate the real synthetic data in the repository.
    We copy the seed data to a temporary directory and point the config there.
    """
    # Find original path
    original_path = Path(settings.synthetic_data_path)
    if not original_path.is_absolute():
        backend_dir = Path(__file__).resolve().parents[1]
        original_path = (backend_dir / original_path).resolve()

    # Create temp dir
    temp_dir = tempfile.mkdtemp()
    
    # Copy data
    if original_path.exists():
        for item in os.listdir(original_path):
            s = original_path / item
            d = Path(temp_dir) / item
            if s.is_dir():
                shutil.copytree(s, d)
            else:
                shutil.copy2(s, d)

    # Override setting
    old_path = settings.synthetic_data_path
    old_compliance = settings.compliance_export_path
    old_feedback = settings.feedback_export_path
    old_readiness = settings.readiness_report_export_path
    
    settings.synthetic_data_path = temp_dir
    settings.compliance_export_path = str(Path(temp_dir) / "exports" / "compliance")
    settings.feedback_export_path = str(Path(temp_dir) / "exports" / "feedback_eval_dataset.json")
    settings.readiness_report_export_path = str(Path(temp_dir) / "exports" / "readiness")

    yield

    # Restore and cleanup
    settings.synthetic_data_path = old_path
    settings.compliance_export_path = old_compliance
    settings.feedback_export_path = old_feedback
    settings.readiness_report_export_path = old_readiness
    shutil.rmtree(temp_dir)
