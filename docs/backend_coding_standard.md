# KnowGap Backend Coding Standards

## 1. General Code Structure
- **Imports**: Group imports in the following order:
  1. Standard library imports.
  2. Third-party imports.
  3. Local application imports (e.g., from `utils`, `config`).
  
  Add a blank line between each group to enhance readability.
- **Modules**: Separate classes and functions by two blank lines, and use one blank line between methods inside a class.

## 2. Asynchronous Code
- **Async/Await Usage**: Use asynchronous code for database queries and I/O operations to ensure non-blocking behavior. Consistently use `await` for MongoDB interactions (e.g., `find_one()`, `update_one()`).
- **Function Naming**: Prefix all async functions with verbs that describe their actions clearly (e.g., `get_user`, `add_user_token`).

## 3. Error Handling
- **Database Operations**: Add error handling for database operations. Wrap MongoDB interactions with `try`/`except` blocks to handle potential connection or operation failures.
- **Routes**: Return meaningful error messages when required parameters are missing or operations fail. Use appropriate status codes (e.g., 400 for bad requests, 404 for not found, 500 for server errors).

## 4. Logging
- Implement logging for significant actions, especially for:
  - User authentication operations.
  - Database modifications (e.g., adding or updating user tokens).
  - Errors and exceptions.
  
  Use Python's `logging` module to capture these actions, which can help in debugging and monitoring.

## 5. Naming Conventions
- **Variables**: Use `snake_case` for variable and function names.
- **Constants**: Use `UPPER_SNAKE_CASE` for constants (e.g., `HEX_ENCRYPTION_KEY`).
- **Functions**: Use descriptive names to convey the purpose of the function, including relevant details (e.g., `add_user_token`, `update_video_link`).

## 6. Database Interaction
- **MongoDB Connections**: Keep database connection settings centralized (e.g., in a `Config` or `.env` file) to avoid hardcoding sensitive information.
- **Collections**: Access collections through variables to improve readability and maintainability (e.g., `db[Config.TOKENS_COLLECTION]`).
- **Upsert Operations**: When using `update_one` with `upsert=True`, clearly document the expected behavior.

## 7. Documentation
- **Docstrings**: Add docstrings to all functions to describe their purpose, parameters, and return values. Use triple quotes (`"""`) for docstrings.
- **Comments**: Add inline comments where necessary to explain non-obvious code logic, especially in encryption, decryption, or data transformation logic.

## 8. Code Formatting
- **PEP 8**: Follow PEP 8 guidelines for formatting (e.g., line length should be <= 79 characters, use 4 spaces per indentation level).
- **Linting**: Use a linter like `flake8` or `pylint` to maintain code quality. Integrate linting checks in the CI/CD pipeline to catch formatting and styling issues before merging.

## 9. Security Best Practices
- **Secrets Management**: Store secrets (e.g., encryption keys, database credentials) in environment variables or secret management services, not directly in the code.
- **Encryption/Decryption**: Ensure sensitive data is encrypted before storing it in the database. Use functions like `encrypt_token` and `decrypt_token` consistently and document the encryption methodology.

## 10. Routes and APIs
- **HTTP Methods**: Use the appropriate HTTP method for each route (e.g., `POST` for creating resources, `GET` for retrieving).
- **Request Validation**: Validate all incoming request data to ensure required fields are present. Return clear error messages when validation fails.
- **JSON Responses**: Return JSON responses consistently, even for errors. Use Flask's `jsonify()` to serialize responses.

---

These standards should help improve the readability, maintainability, and reliability of the KnowGap backend codebase. Feel free to expand on these guidelines or suggest modifications based on team preferences.
