from samvnstock.core.normalize import remap, to_float, to_int


def test_remap_renames_keys_and_drops_unmapped() -> None:
    raw = {"matchPrice": 10.5, "matchVol": 100, "unmapped": "x"}
    field_map = {"matchPrice": "price", "matchVol": "volume"}

    assert remap(raw, field_map) == {"price": 10.5, "volume": 100}


def test_to_float_handles_common_broker_formats() -> None:
    assert to_float("1,234.5") == 1234.5
    assert to_float("") is None
    assert to_float("-") is None
    assert to_float(None) is None
    assert to_float(10) == 10.0


def test_to_int_truncates_float_strings() -> None:
    assert to_int("1,234") == 1234
    assert to_int(None) is None
    assert to_int(10.9) == 10
