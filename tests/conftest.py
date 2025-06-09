from pathlib import Path
import logging
import json
import sys

import pytest

HERE = Path(__file__).resolve().parent
SRCDIR = HERE.parent / 'src'
sys.path.insert(0, str(SRCDIR))


logging.basicConfig(level=logging.INFO)
logging.getLogger('httpx').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


@pytest.fixture(scope='session')
def log():
    return logger


def load_test_data(data_type: str) -> list[dict]:
    path = Path(__file__).parent / f'fixtures/{data_type}.json'
    return json.loads(path.read_text(encoding='utf-8'))


@pytest.fixture
def cpe_data():
    return load_test_data('cpe')
