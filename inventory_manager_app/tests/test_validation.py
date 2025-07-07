import pytest

from inventory_manager_app.core.utils.validation import validate_drive_folder_id


def test_validate_drive_folder_id_valid() -> None:
    assert validate_drive_folder_id("abc-DEF_123") == "abc-DEF_123"


def test_validate_drive_folder_id_invalid_characters() -> None:
    with pytest.raises(Exception):
        validate_drive_folder_id("invalid!")
