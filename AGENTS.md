# AGENTS.md

This document defines the AI agent architecture used in this repository.
Each agent encapsulates a single, well-defined responsibility,
code generation, review, documentation, or vulnerability analysis,
and operates through reproducible workflows built on LLMs and local tools.

## Project overview

This project is the toolsets for cli operations.

## Build and test commands

- Run 'uv build' to build the Python package.
- Run 'uv run pytest' at the project root to run the tests.

### Dev environment

- Use 'uv add' to add Python packages to the dependencies of this project.
- Run 'uv sync' to synchronize the Python environment after
  cloning this repository or modifying pyproject.toml.

## Code style guidelines

### Python style guides

#### Naming

| Type                       | Public             | Internal                         |
| -------------------------- | ------------------ | -------------------------------- |
| Packages                   | lower_with_under   |                                  |
| Modules                    | lower_with_under   | \_lower_with_under               |
| Classes                    | CapWords           | \_CapWords                       |
| Exceptions                 | CapWords           |                                  |
| Functions                  | lower_with_under() | \_lower_with_under()             |
| Global/Class Constants     | CAPS_WITH_UNDER    | \_CAPS_WITH_UNDER                |
| Global/Class Variables     | lower_with_under   | \_lower_with_under               |
| Instance Variables         | lower_with_under   | \_lower_with_under (protected)   |
| Method Names               | lower_with_under() | \_lower_with_under() (protected) |
| Function/Method Parameters | lower_with_under   |                                  |
| Local Variables            | lower_with_under   |                                  |

#### Docstrings

- Use Google style for docstrings.

#### Packages

- Use the absolute imports.

### Git commit messages

- Create git commit messages based on the result of `git diff --cached`.
- Use the conventional commit format, the commit message should be structured as follows:

  '''
  <type>[optional scope]: <description>

  [optional body]

  [optional footer(s)]
  '''

- The first line is the commit title and should be concise.
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

## Testing instructions

This project needs no tests.

## Security considerations

- No passwords or secrets must not be written in any scripts.
