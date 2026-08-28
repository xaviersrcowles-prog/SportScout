import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.validate_data import validate


def test_seed_dataset_is_valid():
    assert validate() == []
