import pytest
from redis.asyncio import Redis

from backend.adapters.mapping_service import MappingService
from backend.infrastructure.glpi.glpi_session import GLPISession


@pytest.mark.asyncio
async def test_initialize_fetches_all_mappings(mocker):
    session = mocker.Mock(spec=GLPISession)
    index_all = mocker.AsyncMock(
        side_effect=[
            [{"id": 1, "name": "Alice"}],
            [{"id": 10, "name": "Support"}],
            [{"id": 2, "name": "Hardware"}],
            [],
            [],
        ]
    )

    redis_client = mocker.Mock(spec=Redis)
    redis_client.hgetall = mocker.AsyncMock(return_value={})
    pipe = mocker.AsyncMock()
    pipe.__aenter__.return_value = pipe
    redis_client.pipeline.return_value = pipe
    mocker.patch.object(MappingService, "_index_all", index_all)

    svc = MappingService(session, redis_client=redis_client)
    await svc.initialize()

    assert svc.lookup("users", 1) == "Alice"
    assert svc.lookup("groups", 10) == "Support"
    assert svc.lookup("categories", 2) == "Hardware"
    assert svc.lookup("locations", 99) is None
    pipe.hset.assert_called()  # ensure caching attempted


@pytest.mark.asyncio
async def test_get_user_map_cache_hit(mocker):
    session = mocker.Mock(spec=GLPISession)
    redis_client = mocker.Mock(spec=Redis)
    redis_client.hgetall = mocker.AsyncMock(return_value={"5": "Alice"})
    index_all = mocker.AsyncMock()
    mocker.patch.object(MappingService, "_index_all", index_all)
    svc = MappingService(session, redis_client=redis_client)

    result = await svc.get_user_map()

    assert result == {5: "Alice"}
    index_all.assert_not_called()


@pytest.mark.asyncio
async def test_get_user_map_cache_miss(mocker):
    session = mocker.Mock(spec=GLPISession)
    index_all = mocker.AsyncMock(return_value=[{"id": 5, "name": "Bob"}])
    mocker.patch.object(MappingService, "_index_all", index_all)
    redis_client = mocker.Mock(spec=Redis)
    redis_client.hgetall = mocker.AsyncMock(return_value={})
    pipe = mocker.AsyncMock()
    pipe.__aenter__.return_value = pipe
    redis_client.pipeline.return_value = pipe

    svc = MappingService(session, redis_client=redis_client)
    result = await svc.get_user_map()

    assert result == {5: "Bob"}
    index_all.assert_awaited_once_with("User")
    pipe.hset.assert_called_once()
    pipe.expire.assert_called_once_with("glpi:mappings:users", svc.cache_ttl_seconds)
