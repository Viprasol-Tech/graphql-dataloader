"""Part of GraphQL DataLoader by Viprasol Tech Private Limited (https://viprasol.com).

Runnable demo proving the DataLoader collapses N author lookups into one
batched backend call. Run with: ``python examples/demo.py``.
"""

from __future__ import annotations

import asyncio

from graphql_dataloader.schema import (
    make_user_loader,
    resolve_post_author,
    resolve_posts,
)
from graphql_dataloader.source import InMemoryUserSource


async def main() -> None:
    source = InMemoryUserSource.seeded()

    # Naive resolution: one backend call per post author (the N+1 problem).
    source.reset_counts()
    posts = await resolve_posts(source)
    for post in posts:
        await source.get_user(post.author_id)
    print(f"Naive:   {len(posts)} posts -> {source.single_call_count} backend calls")

    # Batched resolution through the DataLoader: a single backend call.
    source.reset_counts()
    loader = make_user_loader(source)
    authors = await asyncio.gather(
        *(resolve_post_author(post, loader) for post in posts)
    )
    names = [a.name if a else "?" for a in authors]
    print(f"Batched: {len(posts)} posts -> {source.batch_call_count} backend call")
    print(f"Authors: {names}")


if __name__ == "__main__":
    asyncio.run(main())
