# Random Coffee Bot

A FastAPI-based bot for organizing random coffee meetings.

## Features

- RESTful API built with FastAPI
- Automated code quality checks with Ruff
- Type checking with mypy
- Pre-commit hooks for code consistency

## Requirements

- Python 3.13+
- uv (package manager)

## Installation

1. Clone the repository:
```
bash
git clone https://gitlab.com/FrostWillmott/RandomCoffeeBot.git
cd RandomCoffeeBot
```
2. Create and activate virtual environment:
```
bash
uv venv
source .venv/bin/activate  # On macOS/Linux
```
3. Install dependencies:
```
bash
uv pip install -r requirements.txt
```
4. Install pre-commit hooks:
```
bash
uv pip install pre-commit
pre-commit install
```
## Usage

Run the application:
```bash
uvicorn main:app --reload
```
```


The API will be available at `http://localhost:8000`

### API Endpoints

- `GET /` - Root endpoint, returns a greeting
- `GET /hello/{name}` - Greet a specific user

### Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Development

### Code Quality

This project uses:
- **Ruff** for linting and formatting
- **mypy** for static type checking
- **pre-commit** for automated checks before commits

Run checks manually:
```shell script
ruff check .
ruff format .
mypy .
```


### Pre-commit

Pre-commit hooks run automatically on `git commit`. To run on all files:
```shell script
pre-commit run --all-files
```


## Project Structure

```
RandomCoffeeBot/
├── main.py              # FastAPI application
├── ruff.toml            # Ruff configuration
├── pyproject.toml       # Project metadata
├── .pre-commit-config.yaml  # Pre-commit hooks
└── .gitignore           # Git ignore rules
```


## License

MIT

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Ensure all pre-commit checks pass
5. Submit a merge request
```
