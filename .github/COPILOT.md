# GitHub Copilot & AI Development Instructions

When working with this codebase using GitHub Copilot or other AI coding assistants, follow these guidelines:

## 1. Device Communication
- Serial and Telnet connectors inherit from `Connector` ABC
- All device commands must handle timeouts and connection errors
- Use prompt detection for reliable response parsing
- Always properly encode/decode command strings

## 2. Error Handling
- Use custom exceptions for specific error cases
- Implement proper connection state checking
- Log errors with appropriate severity levels
- Clean up resources in error cases

## 3. Project Structure
- Core MCP logic in `src/core`
- Device connectors in `src/device`
- Server implementation in `src/server`
- Test files mirror source structure in `tests/`

## 4. Type Safety
- All public methods should have type hints
- Use Optional[] for nullable parameters
- Document raised exceptions in docstrings
- Follow interface contracts defined in base classes

## 5. Best Practices
- Use logging instead of print statements
- Implement proper resource cleanup
- Follow PEP 8 style guidelines
- Add tests for new functionality
