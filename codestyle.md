This code style is based on: PEP 8 -- Style Guide for Python Code (https://peps.python.org/pep-0008/)

# Backend Code Style (Python / Flask)

The Python code in this repository follows the official
[PEP 8](https://peps.python.org/pep-0008/) style guide, combined with the
Flask practices below. All committed code must satisfy these rules.

## 1. Naming

- Variable, function and module names: `snake_case`
  (e.g. `validate_expression`).
- Class names: `PascalCase` (e.g. `Calculation`, `CalculatorError`).
- Constants: `UPPER_SNAKE_CASE` (e.g. `MAX_HISTORY_RECORDS`).
- Private functions / variables: leading single underscore
  (e.g. `_check_operators`).

## 2. Formatting

- No line longer than 79 characters.
- Use 4 spaces for indentation; tabs are forbidden.
- Two blank lines between top-level definitions, one blank line between
  methods inside a class.
- One space on each side of binary operators.
- Keep a single trailing newline at the end of the file.

## 3. Comments and Docstrings

- Every module must start with a module docstring.
- Every public function, class and public method must have a docstring
  describing its purpose, arguments (Args) and return value (Returns);
  document Raises when it may raise.
- Comments are written in English, kept concise, and explain "why"
  rather than "what".

## 4. Imports

- Group imports as **standard library -> third party -> local modules**,
  with one blank line between groups.
- Sort alphabetically within each group.
- Wildcard imports (`from x import *`) are forbidden.

## 5. Security and Error Handling

- It is **forbidden** to use `eval()`, `exec()`, `__import__()` or any
  equivalent arbitrary-code-execution method on user input; expressions
  are evaluated safely with `ast`.
- Every API route must use `try-except`, log the error and return a
  standard JSON error response. Never return a traceback to the front
  end.
- Use proper HTTP status codes (200 / 204 / 400 / 404 / 500).

## 6. Database

- Use the Flask-SQLAlchemy session (`db.session`) for CRUD and call
  `commit()` explicitly after modifications.
- Model helper methods return JSON-serializable dictionaries whose field
  names match the API contract.
