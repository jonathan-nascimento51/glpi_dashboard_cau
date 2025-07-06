import pytest

from glpi_dashboard.acl import MappingService
from glpi_dashboard.services.glpi_session import GLPISession


@pytest.mark.asyncio
async def test_initialize_fetches_all_mappings(mocker):
    session = mocker.Mock(spec=GLPISession)
    session.get_all = mocker.AsyncMock(
        side_effect=[
            [{"id": 1, "name": "Alice"}],
            [{"id": 10, "name": "Support"}],
            [{"id": 2, "name": "Hardware"}],
            [],
            [],
        ]
    )

    svc = MappingService(session)
    await svc.initialize()

    assert svc.lookup("users", 1) == "Alice"
    assert svc.lookup("groups", 10) == "Support"
    assert svc.lookup("categories", 2) == "Hardware"
    assert svc.lookup("locations", 99) is None
