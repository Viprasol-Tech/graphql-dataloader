"""Offline tests for the GraphQL schema / plain-function fallback layer."""

from __future__ import annotations

import asyncio

import pytest

from graphql_dataloader import schema as schema_module
from graphql_dataloader.schema import (
    HAS_STRAWBERRY,
    build_schema,
    make_user_loader,
)
from graphql_dataloader.source import InMemoryUserSource


async def test_make_user_loader_batches() -> None:
    source = InMemoryUserSource.seeded()
    loader = make_user_loader(source)
    users = await loader.load_many([1, 2, 3])
    assert [u.name for u in users if u] == ["Ada", "Grace", "Linus"]
    assert source.batch_call_count == 1


def test_build_schema_behaviour_matches_flag() -> None:
    if HAS_STRAWBERRY:
        schema = build_schema()
        assert schema is not None
    else:
        with pytest.raises(RuntimeError, match="strawberry"):
            build_schema()


@pytest.mark.skipif(not HAS_STRAWBERRY, reason="strawberry not installed")
def test_strawberry_query_batches_authors() -> None:
    source = InMemoryUserSource.seeded()
    loader = make_user_loader(source)
    schema = build_schema()
    query = "{ posts { title author { name } } }"
    result = asyncio.run(
        schema.execute(
            query,
            context_value={"source": source, "user_loader": loader},
        )
    )
    assert result.errors is None
    assert result.data is not None
    assert len(result.data["posts"]) == 5
    # Every author resolved through one batched backend call.
    assert source.batch_call_count == 1


def test_has_strawberry_is_bool() -> None:
    assert isinstance(schema_module.HAS_STRAWBERRY, bool)
