# LLM Build Platform

An automated system that accepts task briefs, generates web applications using an LLM, publishes them to GitHub Pages, and reports deployment metadata back to instructor evaluation services.

## Features

- FastAPI endpoint that validates signed JSON build requests
- LLM-assisted project scaffolding with workspace materialization
- GitHub repository automation (MIT license, README, Pages enablement)
- Evaluation endpoint notifications with retry/backoff handling
- SQLite-backed logging of tasks and repo submissions using SQLModel
- CLI and prototype instructor scripts for round handling and evaluation

## Getting Started

### Prerequisites

- Python 3.11+
- Git installed locally
- GitHub personal access token with `repo` and `pages:write` scopes

### Installation

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -e .[dev]
cp .env.example .env
```

Populate `.env` with your GitHub owner, PAT, shared secret, and OpenAI configuration.

### Running the API

```bash
uvicorn app.main:app --reload
```

POST a build task using curl or the provided instructor scripts.

### CLI Utilities

```bash
python -m app.cli init-database
python -m app.cli run-build payload.json
```

## Testing

```bash
pytest
```

## License

MIT

