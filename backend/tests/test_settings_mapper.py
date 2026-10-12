"""Tests for Duckling settings ↔ docling-serve options mapping."""

from config import DEFAULT_CONVERSION_SETTINGS
from services.settings_mapper import (
    convert_options_to_duckling_settings,
    duckling_settings_to_options_dict,
)


def test_maps_ocr_and_table_defaults():
    options = duckling_settings_to_options_dict(DEFAULT_CONVERSION_SETTINGS)
    assert options["do_ocr"] is True
    assert options["table_mode"] == "accurate"
    assert options["pipeline"] == "standard"
    assert "markdown" in options["to_formats"]


def test_maps_page_range_and_formats():
    settings = {
        **DEFAULT_CONVERSION_SETTINGS,
        "page_range": [1, 5],
        "requested_output_formats": ["markdown", "yaml"],
    }
    options = duckling_settings_to_options_dict(settings)
    assert options["page_range"] == [1, 5]
    assert options["to_formats"] == ["markdown", "yaml"]


def test_inverse_roundtrip_core_fields():
    options = duckling_settings_to_options_dict(DEFAULT_CONVERSION_SETTINGS)
    settings = convert_options_to_duckling_settings(options)
    assert settings["ocr"]["enabled"] == options["do_ocr"]
    assert settings["pipeline"]["kind"] == options["pipeline"]
