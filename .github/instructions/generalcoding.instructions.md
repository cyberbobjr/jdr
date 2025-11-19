---
applyTo: "**"
---

# Instructions for Code Documentation

[README.md](../../README.md) contain the information about the Project
Description and documentation should be written in English.
Methods name, class names, and variable names should be in English.

## Code documentation standards

Each method should be documented with a description of its purpose, parameters, and return values. Use the following format:

```markdown
### Method Name

**Description:** Briefly describe what the method does.
**Parameters:**

- `param1` (type): Description of the first parameter.
- `param2` (type): Description of the second parameter.
  **Returns:** Description of the return value, including its type.

### Example Method

**Description:** This method serves as an example of how to document methods in the codebase.
**Parameters:**

- `exampleParam` (string): An example parameter to illustrate the documentation format.
  **Returns:** A string that is a formatted example message.
```

## Actions after code generation

When a new file is created, ensure that:

- The file is added to the appropriate directory structure in the [README.md](../../README.md) file
- The goal of the file is written in the [README.md](../../README.md) file
- Ensure that a corresponding test file is created in the appropriate test directory (`/back/tests`).
- For each new method created, ensure that corresponding unit tests are written in the test file.

# Project general coding standards

## Naming Conventions

- Use PascalCase for component names, interfaces, and type aliases
- Use camelCase for variables, functions, and methods
- Prefix private class members with underscore (\_)
- Use ALL_CAPS for constants

## Type Annotations

- **MANDATORY**: Use type hints everywhere. ALL variables, parameters, return types, and class properties MUST have explicit type annotations. No exceptions.
- Use `List[T]` instead of `list` for better clarity and specificity.
- For return types, always specify the exact type, e.g., `List[ModelMessage]` or `List[Dict[str, Any]]` instead of generic `list`.
- Import types from `typing` (e.g., `List`, `Dict`, `Any`, `Optional`) and specific modules as needed.
- Use `from __future__ import annotations` in files where forward references are needed to avoid import issues.
- Type all local variables in methods where the type is not immediately obvious, e.g., `history: List[ModelMessage] = ModelMessagesTypeAdapter.validate_python(data)`.
- **FORBIDDEN**: Never use import fallbacks (e.g., try/except ImportError with None assignments). Let imports fail naturally if dependencies are missing.
- When using conditional imports (e.g., for optional dependencies), use `TYPE_CHECKING` to import types only for static analysis, ensuring runtime compatibility.

## Error Handling

- Use try/catch blocks for async operations
- Implement proper error boundaries in React components
- Always log errors with contextual information

# FUNCTIONAL Description

All games rules are described in the [synthese_rules.md](../../synthese_rules.md) file.
