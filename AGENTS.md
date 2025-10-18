# AGENTS.md

This document defines the AI agent architecture used in this repository.
Each agent encapsulates a single, well-defined responsibility,
code generation, review, documentation, or vulnerability anlysis,
and operates through reporducible workflows build on LLMs and local tools.

## Project Over overview

## Build and test commands

- Run 'uv build' to build the Python package.
- Run 'uv run pytest' at the project root to run the tests.

### Dev environment

- Use 'uv add' to add Python packages to the dependencies of this project.
- Run 'uv sync' to syncronize the Python environment after
  cloning this repository or modifing pyproject.toml.

## Code style guidelines

### Git commit messages

- Create git commit messages based on the result of `git diff --cached`.
- Use the conventional commit format, the commit message should be structured as follows:

  '''
  <type>[optional scope]: <description>

  [optional body]

  [optional footer(s)]
  '''

- The first line is the commit title and should be concise
- The length of the first line must be at most 50 characters.
- The third line is optional and can provide additional context or details about the change.
- The type in the first line must be one of the following:
  - build: Changes that affect the build system or external dependencies
  - ci: Changes to our CI configuration files and scripts
  - docs: Documentation only changes
  - feat: A new feature
  - fix: A bug fix
  - perf: A code change that improves performance
  - refactor: A code change that neither fixes a bug nor adds a feature
  - style: Changes that do not affect the meaning of the code
  - test: Adding missing tests or correcting existing tests
