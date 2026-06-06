"""Offline tests for the generic DataLoader batching + caching behaviour."""

from __future__ import annotations

import asyncio

import pytest

from graphql_dataloader.dataloader import DataLoader


async def test_load_returns_value() -> None:
    loader: DataLoader[int, int] = DataLoader(lambda keys: _double(keys))
    assert await loader.load(2) == 4


async def test_batches_concurrent_loads_into_single_call() -> None:
    calls: list[list[int]] = []

    async def batch(keys: list[int]) -> list[int]:
        calls.append(list(keys))
        return [k * 10 for k in keys]

    loader: DataLoader[int, int] = DataLoader(batch)
    results = await asyncio.gather(loader.load(1), loader.load(2), loader.load(3))
    assert results == [10, 20, 30]
    assert len(calls) == 1
    assert calls[0] == [1, 2, 3]


async def test_load_many_single_batch() -> None:
    calls: list[list[int]] = []

    async def batch(keys: list[int]) -> list[int]:
        calls.append(list(keys))
        return [k + 1 for k in keys]

    loader: DataLoader[int, int] = DataLoader(batch)
    assert await loader.load_many([5, 6, 7]) == [6, 7, 8]
    assert len(calls) == 1


async def test_cache_avoids_second_backend_call() -> None:
    calls: list[list[int]] = []

    async def batch(keys: list[int]) -> list[int]:
        calls.append(list(keys))
        return list(keys)

    loader: DataLoader[int, int] = DataLoader(batch)
    assert await loader.load(1) == 1
    assert await loader.load(1) == 1
    assert len(calls) == 1


async def test_duplicate_keys_in_same_tick_dedup() -> None:
    calls: list[list[int]] = []

    async def batch(keys: list[int]) -> list[int]:
        calls.append(list(keys))
        return list(keys)

    loader: DataLoader[int, int] = DataLoader(batch)
    results = await asyncio.gather(loader.load(1), loader.load(1), loader.load(2))
    assert results == [1, 1, 2]
    assert len(calls) == 1
    assert calls[0] == [1, 2]


async def test_clear_forces_refetch() -> None:
    calls: list[list[int]] = []

    async def batch(keys: list[int]) -> list[int]:
        calls.append(list(keys))
        return list(keys)

    loader: DataLoader[int, int] = DataLoader(batch)
    await loader.load(1)
    loader.clear(1)
    await loader.load(1)
    assert len(calls) == 2


async def test_clear_all() -> None:
    calls: list[list[int]] = []

    async def batch(keys: list[int]) -> list[int]:
        calls.append(list(keys))
        return list(keys)

    loader: DataLoader[int, int] = DataLoader(batch)
    await loader.load(1)
    loader.clear_all()
    await loader.load(1)
    assert len(calls) == 2


async def test_prime_skips_backend() -> None:
    calls: list[list[int]] = []

    async def batch(keys: list[int]) -> list[int]:
        calls.append(list(keys))
        return list(keys)

    loader: DataLoader[int, int] = DataLoader(batch)
    loader.prime(99, 1234)
    assert await loader.load(99) == 1234
    assert calls == []


async def test_cache_disabled_refetches() -> None:
    calls: list[list[int]] = []

    async def batch(keys: list[int]) -> list[int]:
        calls.append(list(keys))
        return list(keys)

    loader: DataLoader[int, int] = DataLoader(batch, cache=False)
    await loader.load(1)
    await loader.load(1)
    assert len(calls) == 2


async def test_max_batch_size_splits() -> None:
    calls: list[list[int]] = []

    async def batch(keys: list[int]) -> list[int]:
        calls.append(list(keys))
        return list(keys)

    loader: DataLoader[int, int] = DataLoader(batch, max_batch_size=2)
    await loader.load_many([1, 2, 3, 4, 5])
    assert [len(c) for c in calls] == [2, 2, 1]


async def test_error_propagates() -> None:
    async def batch(keys: list[int]) -> list[int]:
        raise RuntimeError("boom")

    loader: DataLoader[int, int] = DataLoader(batch)
    with pytest.raises(RuntimeError, match="boom"):
        await loader.load(1)


async def test_length_mismatch_raises() -> None:
    async def batch(keys: list[int]) -> list[int]:
        return [1]

    loader: DataLoader[int, int] = DataLoader(batch)
    with pytest.raises(ValueError, match="values for"):
        await asyncio.gather(loader.load(1), loader.load(2))


def test_negative_max_batch_size_rejected() -> None:
    with pytest.raises(ValueError, match="max_batch_size"):
        DataLoader(_double, max_batch_size=-1)


async def _double(keys: list[int]) -> list[int]:
    return [k * 2 for k in keys]
