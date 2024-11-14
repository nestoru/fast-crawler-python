# Fast Crawler

A Python based high-performance web crawler with support for concurrent processing.

## Installation

```bash
# Install with Poetry
poetry install
```

## Usage

```bash
# Activate the poetry environment
poetry shell

# Run the crawler
fast-crawler https://example.com --same-domain-only --max-concurrent-processes 5 --error-level DEBUG
```

OR run it directly from poetry:
```bash
poetry run fast-crawler https://example.com --same-domain-only --max-concurrent-processes 5 --error-level DEBUG
```

## Features

- Concurrent web crawling
- Domain and subdomain filtering
- Configurable concurrency level
- Comprehensive logging system
- Performance metrics tracking

## Development

```bash
# Run tests
poetry run pytest

# Format code
poetry run black fast_crawler
poetry run isort fast_crawler

# Lint code
poetry run flake8 fast_crawler
```

## Sharing all relevant code. Use the following find (fd) command. Pipe the result to the pbcopy command if you want it in the clipboard
```
fd -H -t f --exclude '.git' --exclude '.gitignore' --exclude 'poetry.lock' -0 | xargs -0 -I {} sh -c 'echo "File: {}"; cat {}'

## License

MIT
