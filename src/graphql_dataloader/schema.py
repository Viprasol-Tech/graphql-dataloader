"""Part of GraphQL DataLoader by Viprasol Tech Private Limited (https://viprasol.com).

A small GraphQL layer demonstrating batched resolution. When
``strawberry-graphql`` is installed a real schema is exposed; otherwise the
same resolution logic is available as plain async functions so the example and
tests run fully offline regardless.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from graphql_dataloader.dataloader import DataLoader
from graphql_dataloader.source import InMemoryUserSource, Post, User

try:  # pragma: no cover - import guard exercised by environment
    import strawberry

    HAS_STRAWBERRY = True
except ImportError:  # pragma: no cover - offline fallback
    strawberry = None  # type: ignore[assignment]
    HAS_STRAWBERRY = False


def make_user_loader(source: InMemoryUserSource) -> DataLoader[int, User | None]:
    """Build a DataLoader that batches author lookups against ``source``."""

    async def batch_load(keys: Sequence[int]) -> Sequence[User | None]:
        return await source.get_users(keys)

    return DataLoader(batch_load)


async def resolve_posts(source: InMemoryUserSource) -> list[Post]:
    """Resolver for the ``posts`` query field."""
    return await source.get_posts()


async def resolve_post_author(
    post: Post,
    loader: DataLoader[int, User | None],
) -> User | None:
    """Resolver for ``Post.author`` that loads through the DataLoader."""
    return await loader.load(post.author_id)


if TYPE_CHECKING:
    build_schema: Any
elif HAS_STRAWBERRY:

    @strawberry.type
    class UserType:
        id: int
        name: str

    @strawberry.type
    class PostType:
        id: int
        title: str
        author_id: strawberry.Private[int]

        @strawberry.field
        async def author(self, info: strawberry.Info) -> UserType | None:
            loader: DataLoader[int, User | None] = info.context["user_loader"]
            user = await loader.load(self.author_id)
            if user is None:
                return None
            return UserType(id=user.id, name=user.name)

    @strawberry.type
    class Query:
        @strawberry.field
        async def posts(self, info: strawberry.Info) -> list[PostType]:
            source: InMemoryUserSource = info.context["source"]
            posts = await source.get_posts()
            return [
                PostType(id=p.id, title=p.title, author_id=p.author_id) for p in posts
            ]

    def build_schema() -> strawberry.Schema:
        """Return a Strawberry schema wired to the resolvers above."""
        return strawberry.Schema(query=Query)

else:

    def build_schema() -> Any:
        """Raise when Strawberry is unavailable; use the plain resolvers."""
        raise RuntimeError(
            "strawberry-graphql is not installed; use resolve_posts and "
            "resolve_post_author instead."
        )
