<p align="center"><img src="docs/assets/logo.png" width="120"></p>

# GraphQL DataLoader

> Kill the GraphQL N+1 problem — a generic async batching + caching DataLoader, in pure Python.

*Built and maintained by [Viprasol Tech](https://viprasol.com) — Fintech Experts. Full-Stack Builders.*

![CI](https://img.shields.io/github/actions/workflow/status/Viprasol-Tech/graphql-dataloader/ci.yml?branch=main&style=flat-square)
![MIT](https://img.shields.io/badge/license-MIT-green?style=flat-square)
![Python](https://img.shields.io/badge/python-3.11%2B-blue?style=flat-square)
![Ruff](https://img.shields.io/badge/lint-ruff-261230?style=flat-square)
![Telegram](https://img.shields.io/badge/Telegram-viprasol__help-26A5E4?style=flat-square)
![Stars](https://img.shields.io/github/stars/Viprasol-Tech/graphql-dataloader?style=flat-square)

The classic GraphQL N+1 problem: resolving a list of N posts triggers N separate
backend calls to fetch each post's author. This library coalesces those N loads,
happening in the same event-loop tick, into a **single** batched backend call —
and caches per key so repeats are free.

## ✨ Features

- ⚡ **Async batching** — coalesces same-tick loads into one backend call.
- 🧠 **Per-key caching** — never fetch the same key twice.
- 🧮 **Call-counting data source** — *prove* N calls collapsed into 1.
- 🔢 **Configurable batch size** — cap dispatch with `max_batch_size`.
- 🧩 **Generic & type-safe** — `DataLoader[K, V]` with full typing.
- 🍓 **Strawberry GraphQL** — real schema when installed, plain resolvers when not.
- 📴 **Fully offline** — runs and tests with zero network.
- 🌱 **Seed & prime** — pre-load known values into the cache.
- 🧹 **Cache control** — `clear`, `clear_all`, `prime` helpers.
- 🛡️ **mypy strict** — clean under the strictest type checking.
- 🧪 **12+ tests** — asserting exact batch/call counts.
- 🐳 **Dockerfile** — reproducible runs anywhere.

## 🚀 Quickstart

```bash
git clone https://github.com/Viprasol-Tech/graphql-dataloader.git
cd graphql-dataloader
python -m pip install -e ".[dev,graphql]"
python examples/demo.py
python -m pytest
```

## 🧑‍💻 Usage

```python
import asyncio
from graphql_dataloader import DataLoader, InMemoryUserSource


async def main() -> None:
    source = InMemoryUserSource.seeded()

    async def batch_load(keys):
        return await source.get_users(keys)

    loader = DataLoader(batch_load)
    # Five concurrent loads, three distinct keys -> ONE backend call.
    users = await asyncio.gather(loader.load(1), loader.load(2), loader.load(1))
    print([u.name for u in users])  # ['Ada', 'Grace', 'Ada']
    print(source.batch_call_count)  # 1


asyncio.run(main())
```

## 🗺️ Roadmap

- [x] Generic async batching + caching DataLoader
- [x] Call-counting in-memory data source
- [x] Strawberry GraphQL schema with offline fallback
- [ ] Pluggable cache backends (Redis, LRU)
- [ ] Per-request loader context helper
- [ ] Tracing / metrics hooks

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) and our
[Code of Conduct](CODE_OF_CONDUCT.md) before opening a PR.

## 📬 Contact — Viprasol Tech Private Limited

- 🌐 Website: [viprasol.com](https://viprasol.com)
- ✉️ Email: [support@viprasol.com](mailto:support@viprasol.com)
- 💬 Telegram: [t.me/viprasol_help](https://t.me/viprasol_help) · 📱 WhatsApp: +91 96336 52112
- 🐙 GitHub: [@Viprasol-Tech](https://github.com/Viprasol-Tech) · 💼 [LinkedIn](https://www.linkedin.com/in/viprasol/) · 𝕏 [@viprasol](https://twitter.com/viprasol)

> *Viprasol Tech — fintech software, algorithmic trading systems, MT4/MT5 bots, AI voice agents, and B2B SaaS. Need a custom build? [Get in touch](mailto:support@viprasol.com).*

## 📄 License

MIT © 2025 Viprasol Tech Private Limited — see [LICENSE](LICENSE).
