"""Part of GraphQL DataLoader by Viprasol Tech Private Limited (https://viprasol.com).

A generic async batching + caching DataLoader that solves the GraphQL N+1
problem, plus an in-memory data source that counts backend calls so you can
prove batching collapses N lookups into a single backend round-trip.
"""

from __future__ import annotations

from graphql_dataloader.dataloader import DataLoader
from graphql_dataloader.schema import (
    HAS_STRAWBERRY,
    resolve_post_author,
    resolve_posts,
)
from graphql_dataloader.source import InMemoryUserSource, Post, User

__all__ = [
    "HAS_STRAWBERRY",
    "DataLoader",
    "InMemoryUserSource",
    "Post",
    "User",
    "resolve_post_author",
    "resolve_posts",
]

__version__ = "0.1.0"
