import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"

for path in [ROOT, BACKEND]:
    path_text = str(path)
    if path_text not in sys.path:
        sys.path.insert(0, path_text)
