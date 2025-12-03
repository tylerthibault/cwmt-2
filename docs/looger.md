# CWMT Logger Usage Guide

## Overview
The CWMT Logger is a wrapper around Python's built-in logging module, providing a simple interface for application-wide logging with consistent formatting and output handling.

## Basic Usage

### Getting a Logger Instance
```python
from src.utils.logger import Logger

# Get the application-wide logger (recommended)
logger = Logger.get_app_logger()

# Or create a custom logger
logger = Logger(name="MyModule", log_file="custom.log")
```

### Logging Messages
```python
# Basic logging
logger.info("User logged in successfully")
logger.warning("Database connection slow")
logger.error("Failed to process request")

# Logging with context
logger.info("User created", user_id=123, email="user@example.com")
logger.error("Validation failed", field="email", value="invalid-email")

# Error logging with exceptions
try:
    # Some operation
    pass
except Exception as e:
    logger.error("Operation failed", error=e, user_id=123)
```

## Integration with CWMT Architecture

### In Logic Layer
```python
# src/logic/user_logic.py
from src.utils.logger import Logger

logger = Logger.get_app_logger()

class UserLogic:
    @staticmethod
    def create_user(data):
        logger.info("Creating new user", email=data.get('email'))
        try:
            # Business logic here
            user = User(**data)
            db.session.add(user)
            db.session.commit()
            
            logger.info("User created successfully", user_id=user.id)
            return user
        except ValidationError as e:
            logger.warning("User creation failed - validation error", error=str(e))
            raise
        except Exception as e:
            logger.error("User creation failed - unexpected error", error=e)
            raise
```

### In Controllers
```python
# src/controllers/routes.py
from src.utils.logger import Logger

logger = Logger.get_app_logger()

@app.route('/users', methods=['POST'])
def create_user():
    logger.debug("Received user creation request")
    try:
        data = request.get_json()
        user = UserLogic.create_user(data)
        logger.info("User creation endpoint success", user_id=user.id)
        return jsonify(user.to_dict()), 201
    except ValidationError as e:
        logger.warning("User creation endpoint - validation error", error=str(e))
        return jsonify({'error': str(e)}), 400
```

## Log Levels

- **DEBUG**: Detailed diagnostic information
- **INFO**: General application flow and business events
- **WARNING**: Something unexpected but not breaking
- **ERROR**: Serious problems that prevented operations
- **CRITICAL**: Very serious errors that may abort the program

## Output

### Console Output
All log messages appear in the console with format:
```
2025-10-12 14:30:15,123 - CWMT - INFO - User created successfully | user_id=123 | email=user@example.com
```

### File Output
Daily log files are automatically created in `logs/cwmt_YYYYMMDD.log` with the same format.

## Best Practices

1. **Use context**: Always include relevant context with kwargs
2. **Log business events**: Track important application flows
3. **Include error details**: Pass exceptions to error() method
4. **Use appropriate levels**: Don't overuse ERROR for validation issues
5. **Keep messages clear**: Write logs for future debugging

## Configuration

The logger automatically:
- Creates the `logs/` directory if it doesn't exist
- Uses daily rotating log files
- Outputs to both console and file
- Prevents duplicate handlers
- Uses INFO level by default

For custom configuration, create a Logger instance with specific parameters:
```python
logger = Logger(
    name="CustomModule",
    log_file="custom.log",
    level=LogLevel.DEBUG
)
```