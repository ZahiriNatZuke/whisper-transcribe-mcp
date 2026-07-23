from __future__ import annotations

import importlib.util
from pathlib import Path


def load_checker():
    path = Path(__file__).parents[1] / "scripts" / "check_release_metadata.py"
    spec = importlib.util.spec_from_file_location("check_release_metadata", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_release_metadata_is_consistent() -> None:
    checker = load_checker()

    assert checker.validate() == []


def test_release_metadata_rejects_wrong_tag() -> None:
    checker = load_checker()

    assert checker.validate(tag="v0.0.0") == [
        f"tag is 'v0.0.0'; expected 'v{checker.project_version()}'"
    ]
