# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-01

### Added

- Generic async `DataLoader[K, V]` with same-tick batching and per-key caching.
- `clear`, `clear_all`, `prime`, `load_many`, and `max_batch_size` support.
- `InMemoryUserSource` that counts single vs. batched backend calls.
- Strawberry GraphQL schema with a plain-function offline fallback.
- Runnable `examples/demo.py` proving N+1 collapses to one batched call.
- 12+ offline tests asserting exact batch/call counts.

[0.1.0]: https://github.com/Viprasol-Tech/graphql-dataloader/releases/tag/v0.1.0
