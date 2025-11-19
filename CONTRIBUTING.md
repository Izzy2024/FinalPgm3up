# Contributing to SIGRAA

Thank you for your interest in contributing to SIGRAA! This document provides guidelines and instructions for contributing to this project.

## Getting Started

1.  **Fork the repository** on GitHub.
2.  **Clone your fork** locally:
    ```bash
    git clone https://github.com/your-username/sigraa.git
    cd sigraa
    ```
3.  **Set up the environment**:
    - Follow the instructions in `README.md` or `CLAUDE.md` to set up the backend and frontend.
    - Run `./start.sh` to verify everything is working.

## Development Workflow

1.  **Create a branch** for your feature or fix:
    ```bash
    git checkout -b feature/amazing-feature
    # or
    git checkout -b fix/critical-bug
    ```
2.  **Make your changes**.
3.  **Run tests** to ensure no regressions:
    - Backend: `pytest`
    - Frontend: `npm test`
4.  **Commit your changes** using conventional commits:
    - `feat: add new login screen`
    - `fix: resolve database connection issue`
    - `docs: update readme`

## Pull Requests

1.  Push your branch to your fork.
2.  Open a Pull Request against the `main` branch.
3.  Describe your changes clearly in the PR description.

## Code Style

- **Backend**: We use `black`, `isort`, and `flake8`. Run `make lint` (if available) or check `CLAUDE.md` for commands.
- **Frontend**: We use `ESLint` and `Prettier`.

## Questions?

Check the `docs/` directory for more detailed documentation on specific parts of the system.
