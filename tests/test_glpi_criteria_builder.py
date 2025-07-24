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


@pytest.mark.asyncio
async def test_load_field_ids():
    class FakeSession:
        async def list_search_options(self, itemtype):
            assert itemtype == "Ticket"
            return {"5": {"name": "Status"}, "12": {"name": "Group"}}

    mapping = await CriteriaBuilder.load_field_ids(FakeSession())
    assert mapping == {"status": 5, "group": 12}
