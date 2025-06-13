---
applyTo: '**'
---
# Instructions for Code Documentation
[README.md](../../README.md) contain the information about the Project

For Haystack, the code documentation are:
[PydanticAi documentation](../../pydanticai.md) (for PydanticAi documentation)
Description and documentation should be written in French.
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
When a new file is generated, ensure that:
- The file is added to the appropriate directory structure in the [README.md](../../README.md) file
- The goal of the file is written in the [README.md](../../README.md) file
- Ensure that a corresponding test file is generated in the appropriate test directory (`/back/tests`).
- For each new method created, ensure that corresponding unit tests are written in the test file.

# Project general coding standards
## Naming Conventions
- Use PascalCase for component names, interfaces, and type aliases
- Use camelCase for variables, functions, and methods
- Prefix private class members with underscore (_)
- Use ALL_CAPS for constants

## Error Handling
- Use try/catch blocks for async operations
- Implement proper error boundaries in React components
- Always log errors with contextual information