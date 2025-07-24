import pytest

from glpi_criteria_builder import CriteriaBuilder


def test_add_simple_alias():
    builder = CriteriaBuilder(field_map={"status": 1})
    builder.where_status("Closed")
    params = builder.build()
    assert params == {"criteria[0][field]": "1", "criteria[0][search]": "Closed"}


def test_unknown_field_alias():
    builder = CriteriaBuilder(field_map={"status": 1})
    with pytest.raises(KeyError):
        builder.add("foo", "bar")
