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

    old_values = {}
    for field_name, value in settings.model_dump().items():
        if isinstance(value, str):
            if value.startswith("data/synthetic/"):
                old_values[field_name] = value
                filename = value.replace("data/synthetic/", "")
                setattr(settings, field_name, str(Path(temp_dir) / filename))
            elif value.startswith("data/exports/"):
                old_values[field_name] = value
                filename = value.replace("data/exports/", "exports/")
                setattr(settings, field_name, str(Path(temp_dir) / filename))
            elif value == "data/archive":
                old_values[field_name] = value
                setattr(settings, field_name, str(Path(temp_dir) / "archive"))
            elif field_name == "synthetic_data_path":
                old_values[field_name] = value
                setattr(settings, field_name, temp_dir)

    yield

    # Restore and cleanup
    for field_name, old_value in old_values.items():
        setattr(settings, field_name, old_value)
    shutil.rmtree(temp_dir)
