import sys
from pathlib import Path

import pytest

TOOLKIT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLKIT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import helpers  # noqa: E402


@pytest.fixture()
def template(tmp_path):
    return helpers.make_template(tmp_path / "template.xlsx")


@pytest.fixture()
def package(tmp_path):
    root = tmp_path / "paket"
    root.mkdir()
    return helpers.make_package(root)
