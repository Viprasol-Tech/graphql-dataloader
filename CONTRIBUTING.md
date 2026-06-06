# Contributing

Thanks for your interest in improving **GraphQL DataLoader**!

## Development setup

```bash
python -m pip install -e ".[dev,graphql]"
```

## Before opening a PR

Run the full local gate — all four must pass:

```bash
python -m ruff check .
python -m ruff format --check .
python -m mypy src
python -m pytest
```

## Guidelines

- Keep the library dependency-free at runtime; GraphQL extras stay optional.
- Add or update tests for any behaviour change — assert exact call counts.
- Match the existing style; `ruff format` is the source of truth.
- One logical change per PR; write a clear description.

By contributing you agree your work is licensed under the MIT License and that
you abide by our [Code of Conduct](CODE_OF_CONDUCT.md).
