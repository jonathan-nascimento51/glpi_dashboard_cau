import pytest

from glpi_criteria_builder import CriteriaBuilder


def test_add_simple():
    builder = CriteriaBuilder(field_map={"status": 1})
    builder.where_status("Closed")
    params = builder.build()
    assert params == {"criteria[0][field]": "1", "criteria[0][search]": "Closed"}


def test_or_link():
    builder = CriteriaBuilder(field_map={"status": 1})
    builder.where_status("New", link="OR").where_status("Pending")
    params = builder.build()
    assert params["criteria[0][link]"] == "OR"
    assert "criteria[1][link]" not in params


def test_unknown_field():
    builder = CriteriaBuilder(field_map={"status": 1})
    with pytest.raises(KeyError):
        builder.add("foo", "bar")


def test_multiple_fields_mixed_links():
    builder = CriteriaBuilder(field_map={"status": 1, "priority": 2, "type": 3})
    (
        builder.where_status("Closed", link="OR")
        .add("priority", "High", link="AND")
        .add("type", "Incident")
    )
    params = builder.build()
    assert params["criteria[0][field]"] == "1"
    assert params["criteria[0][search]"] == "Closed"
    assert params["criteria[0][link]"] == "OR"
    assert params["criteria[1][field]"] == "2"
    assert params["criteria[1][search]"] == "High"
    assert params["criteria[1][link]"] == "AND"
    assert params["criteria[2][field]"] == "3"
    assert params["criteria[2][search]"] == "Incident"
    assert "criteria[2][link]" not in params


@pytest.mark.asyncio
async def test_load_field_ids():
    class FakeSession:
        async def list_search_options(self, itemtype):
            assert itemtype == "Ticket"
            return {"5": {"name": "Status"}, "12": {"name": "Group"}}

    mapping = await CriteriaBuilder.load_field_ids(FakeSession())
    assert mapping == {"status": 5, "group": 12}


@pytest.mark.asyncio
async def test_load_field_ids_cache():
    calls = []

    class FakeSession:
        async def list_search_options(self, itemtype):
            calls.append(itemtype)
            return {"5": {"name": "Status"}}

    CriteriaBuilder._cache.clear()
    mapping1 = await CriteriaBuilder.load_field_ids(FakeSession())
    mapping2 = await CriteriaBuilder.load_field_ids(FakeSession())
    assert mapping1 == mapping2 == {"status": 5}
    assert calls.count("Ticket") == 1
