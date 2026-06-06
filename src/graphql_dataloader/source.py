"""Part of GraphQL DataLoader by Viprasol Tech Private Limited (https://viprasol.com).

An in-memory data source that counts how many times its backend is hit. This
makes the N+1 problem observable: without a DataLoader every author lookup is
a separate backend call, with one they collapse into a single batched call.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class User:
    """A user record returned by the data source."""

    id: int
    name: str


@dataclass(frozen=True, slots=True)
class Post:
    """A post that references its author by ``author_id``."""

    id: int
    title: str
    author_id: int


@dataclass(slots=True)
class InMemoryUserSource:
    """A fake user backend that records every call it receives.

    Two counters are exposed for assertions in tests/examples:

    * ``single_call_count`` — number of one-at-a-time ``get_user`` calls.
    * ``batch_call_count`` — number of batched ``get_users`` calls.
    """

    users: dict[int, User] = field(default_factory=dict)
    posts: list[Post] = field(default_factory=list)
    single_call_count: int = 0
    batch_call_count: int = 0

    @classmethod
    def seeded(cls) -> InMemoryUserSource:
        """Return a source pre-populated with sample users and posts."""
        users = {
            1: User(id=1, name="Ada"),
            2: User(id=2, name="Grace"),
            3: User(id=3, name="Linus"),
        }
        posts = [
            Post(id=10, title="On Algorithms", author_id=1),
            Post(id=11, title="Compilers 101", author_id=2),
            Post(id=12, title="Kernel Notes", author_id=3),
            Post(id=13, title="More Algorithms", author_id=1),
            Post(id=14, title="Even More Compilers", author_id=2),
        ]
        return cls(users=users, posts=posts)

    def reset_counts(self) -> None:
        """Zero both call counters."""
        self.single_call_count = 0
        self.batch_call_count = 0

    async def get_user(self, user_id: int) -> User | None:
        """Fetch a single user, incrementing ``single_call_count``."""
        self.single_call_count += 1
        return self.users.get(user_id)

    async def get_users(self, user_ids: Sequence[int]) -> list[User | None]:
        """Fetch many users in one call, incrementing ``batch_call_count``.

        Results are returned in the same order as ``user_ids``.
        """
        self.batch_call_count += 1
        return [self.users.get(uid) for uid in user_ids]

    async def get_posts(self) -> list[Post]:
        """Return every post (does not affect user call counters)."""
        return list(self.posts)
