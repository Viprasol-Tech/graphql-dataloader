"""Offline tests proving the N+1 collapse using the call-counting source."""

from __future__ import annotations

import asyncio
from collections.abc import Sequence

from graphql_dataloader.schema import (
    make_user_loader,
    resolve_post_author,
    resolve_posts,
)
from graphql_dataloader.source import InMemoryUserSource, User


async def test_naive_resolution_is_n_plus_one() -> None:
    source = InMemoryUserSource.seeded()
    posts = await resolve_posts(source)
    source.reset_counts()
    for post in posts:
        await source.get_user(post.author_id)
    # One backend call per post -> the N+1 problem.
    assert source.single_call_count == len(posts)
    assert source.single_call_count == 5


async def test_dataloader_collapses_to_single_call() -> None:
    source = InMemoryUserSource.seeded()
    posts = await resolve_posts(source)
    source.reset_counts()
    loader = make_user_loader(source)
    await asyncio.gather(*(resolve_post_author(p, loader) for p in posts))
    # All five author lookups collapse into exactly one batched backend call.
    assert source.batch_call_count == 1
    assert source.single_call_count == 0


async def test_dataloader_returns_correct_authors() -> None:
    source = InMemoryUserSource.seeded()
    posts = await resolve_posts(source)
    loader = make_user_loader(source)
    authors = await asyncio.gather(*(resolve_post_author(p, loader) for p in posts))
    names = [a.name for a in authors if a is not None]
    assert names == ["Ada", "Grace", "Linus", "Ada", "Grace"]


async def test_dataloader_keys_are_deduped_in_batch() -> None:
    captured: list[list[int]] = []

    class SpySource(InMemoryUserSource):
        async def get_users(self, user_ids: Sequence[int]) -> list[User | None]:
            captured.append(list(user_ids))
            return await super().get_users(user_ids)

    base = InMemoryUserSource.seeded()
    source = SpySource(users=base.users, posts=base.posts)
    posts = await resolve_posts(source)
    loader = make_user_loader(source)
    await asyncio.gather(*(resolve_post_author(p, loader) for p in posts))
    # Five posts, three distinct authors -> one batch of three unique keys.
    assert len(captured) == 1
    assert sorted(captured[0]) == [1, 2, 3]


async def test_second_resolution_uses_cache() -> None:
    source = InMemoryUserSource.seeded()
    posts = await resolve_posts(source)
    source.reset_counts()
    loader = make_user_loader(source)
    await asyncio.gather(*(resolve_post_author(p, loader) for p in posts))
    await asyncio.gather(*(resolve_post_author(p, loader) for p in posts))
    # The second pass is served entirely from cache: still one backend call.
    assert source.batch_call_count == 1
