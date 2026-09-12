from pathlib import Path
import sys
import pytest

sys.path.insert(0, str(Path(__file__).parents[1]))

@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    import time
    monkeypatch.setattr(time, 'sleep', lambda *args: None)
