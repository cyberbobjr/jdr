---
trigger: always_on
---

**Type Hints**: **MANDATORY**. All functions, methods, variables, class properties, and parameters must have explicit type hints. This includes:

- All function parameters and return types
- All class properties (declared at class level)
- All local variables (inline type annotations)
- All loop variables
- All comprehension variables where ambiguous
  **Example:**

  ```python
  class MyService:
      property_name: str  # Class property type hint
      count: int
      
      def __init__(self, name: str) -> None:
          self.property_name = name
          local_var: int = 42  # Local variable type hint
  ```

- **Pydantic Models**: Use for all data structures. Use V2 features like `field_validator`.
- **Async**: Use `async/await` for all I/O operations.
- **Docstrings**: Document all public methods (description, args, returns).
- **FastAPI Route Documentation**: For all FastAPI router endpoints, provide comprehensive docstrings with detailed descriptions, parameter explanations, request/response JSON examples, and error conditions. This ensures complete OpenAPI documentation for API consumers. Include full JSON schemas for requests and responses to facilitate automatic API documentation generation.
- **Error Handling**: Use custom exceptions from `utils/exceptions.py`.
- **File Naming**:
  - Services: `{domain}_service.py`
  - Managers: `{resource}_manager.py`
  - Tools: `{category}_tools.py`
