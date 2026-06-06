"""Part of GraphQL DataLoader by Viprasol Tech Private Limited (https://viprasol.com).

A generic, type-safe async DataLoader implementing the classic batching +
per-key caching strategy popularised by the JavaScript ``dataloader`` library.

Keys requested within the same event-loop tick are coalesced into a single
call to a user-supplied ``batch_load_fn``. Results are cached per key so that
repeated loads never hit the backend twice.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Hashable, Sequence
from typing import Generic, TypeVar

K = TypeVar("K", bound=Hashable)
V = TypeVar("V")

BatchLoadFn = Callable[[Sequence[K]], Awaitable[Sequence[V]]]


class DataLoader(Generic[K, V]):
    """Batch and cache async loads by key.

    Parameters
    ----------
    batch_load_fn:
        Async function that receives a sequence of unique keys and returns a
        sequence of values *in the same order* as the keys it was given.
    cache:
        When ``True`` (default) results are memoised per key for the lifetime
        of the loader instance.
    max_batch_size:
        Optional cap on how many keys are dispatched in a single batch. A
        value of ``0`` (default) means unlimited.
    """

    def __init__(
        self,
        batch_load_fn: BatchLoadFn[K, V],
        *,
        cache: bool = True,
        max_batch_size: int = 0,
    ) -> None:
        if max_batch_size < 0:
            raise ValueError("max_batch_size must be >= 0")
        self._batch_load_fn = batch_load_fn
        self._cache_enabled = cache
        self._max_batch_size = max_batch_size
        self._cache: dict[K, asyncio.Future[V]] = {}
        self._queue: list[tuple[K, asyncio.Future[V]]] = []
        self._dispatch_scheduled = False

    def load(self, key: K) -> asyncio.Future[V]:
        """Load a single value by ``key``, returning an awaitable future."""
        if self._cache_enabled and key in self._cache:
            return self._cache[key]

        loop = asyncio.get_event_loop()
        future: asyncio.Future[V] = loop.create_future()

        if self._cache_enabled:
            self._cache[key] = future

        self._queue.append((key, future))
        self._schedule_dispatch()
        return future

    async def load_many(self, keys: Sequence[K]) -> list[V]:
        """Load many values, returning results in the order of ``keys``."""
        return await asyncio.gather(*(self.load(key) for key in keys))

    def clear(self, key: K) -> None:
        """Remove a single ``key`` from the cache."""
        self._cache.pop(key, None)

    def clear_all(self) -> None:
        """Remove every entry from the cache."""
        self._cache.clear()

    def prime(self, key: K, value: V) -> None:
        """Seed the cache with a known ``value`` for ``key``."""
        if not self._cache_enabled or key in self._cache:
            return
        loop = asyncio.get_event_loop()
        future: asyncio.Future[V] = loop.create_future()
        future.set_result(value)
        self._cache[key] = future

    def _schedule_dispatch(self) -> None:
        if self._dispatch_scheduled:
            return
        self._dispatch_scheduled = True
        loop = asyncio.get_event_loop()
        loop.call_soon(self._dispatch)

    def _dispatch(self) -> None:
        self._dispatch_scheduled = False
        queue = self._queue
        self._queue = []
        if not queue:
            return

        if self._max_batch_size > 0:
            for start in range(0, len(queue), self._max_batch_size):
                chunk = queue[start : start + self._max_batch_size]
                self._dispatch_batch(chunk)
        else:
            self._dispatch_batch(queue)

    def _dispatch_batch(self, batch: list[tuple[K, asyncio.Future[V]]]) -> None:
        keys = [key for key, _ in batch]
        futures = [future for _, future in batch]
        task = asyncio.ensure_future(self._batch_load_fn(keys))

        def _on_done(completed: asyncio.Future[Sequence[V]]) -> None:
            error = completed.exception()
            if error is not None:
                for future in futures:
                    if not future.done():
                        future.set_exception(error)
                return
            values = completed.result()
            if len(values) != len(keys):
                mismatch = ValueError(
                    f"batch_load_fn returned {len(values)} values for {len(keys)} keys"
                )
                for future in futures:
                    if not future.done():
                        future.set_exception(mismatch)
                return
            for future, value in zip(futures, values, strict=True):
                if not future.done():
                    future.set_result(value)

        task.add_done_callback(_on_done)
