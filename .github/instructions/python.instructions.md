---
applyTo: '**/*.py'
---

# Python Development Instructions for CWMT Flask Application

These instructions enforce the architectural patterns and best practices defined in the project constitution for Python code development.

## Core Architecture Patterns

### Thin Controllers Pattern
Controllers in `src/controllers/routes.py` MUST be thin and handle ONLY:
```python
# ✅ CORRECT - Thin controller
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    user = UserLogic.create_user(data)  # Delegate to logic layer
    return jsonify(user.to_dict()), 201

# ❌ INCORRECT - Business logic in controller
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    # Don't do validation, transformation, or business rules here
    if not data.get('email') or '@' not in data['email']:
        return jsonify({'error': 'Invalid email'}), 400
    # This belongs in logic layer
```

**Controllers should only:**
- Extract request parameters/data
- Call appropriate logic layer functions
- Format and return responses
- Handle HTTP-specific concerns (status codes, headers)

### Thin Models Pattern
Models in `src/models/` MUST be thin SQLAlchemy entities ONLY:
```python
# ✅ CORRECT - Thin model
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Simple serialization only"""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'created_at': self.created_at.isoformat()
        }

# ❌ INCORRECT - Business logic in model
class User(db.Model):
    # ... columns ...
    
    def send_welcome_email(self):  # Business logic - belongs in logic layer
        pass
    
    def calculate_subscription_status(self):  # Complex logic - belongs in logic layer
        pass
```

**Models should only:**
- Define database schema (SQLAlchemy columns, relationships)
- Provide simple serialization methods (`to_dict()`, `from_dict()`)
- Include basic database constraints and validations
- NO business logic, NO complex calculations, NO external service calls

### Thick Logic Layer Pattern
All business logic MUST reside in `src/logic/` modules:
```python
# ✅ CORRECT - Thick logic layer (src/logic/user_logic.py)
class UserLogic:
    @staticmethod
    def create_user(data):
        """Create user with full business logic"""
        # Validation
        if not data.get('email') or '@' not in data['email']:
            raise ValidationError('Invalid email format')
        
        # Business rules
        if UserLogic.email_exists(data['email']):
            raise BusinessError('Email already registered')
        
        # Data transformation
        clean_data = UserLogic._clean_user_data(data)
        
        # Persistence (through thin model)
        user = User(**clean_data)
        db.session.add(user)
        db.session.commit()
        
        # Post-creation logic
        UserLogic._send_welcome_email(user)
        UserLogic._log_user_creation(user)
        
        return user
    
    @staticmethod
    def email_exists(email):
        """Business logic for checking email existence"""
        return User.query.filter_by(email=email).first() is not None
```

## Database and ORM Guidelines

### SQLAlchemy Best Practices
- Use SQLAlchemy declarative base and relationships
- Query through logic layer only
- NO raw SQL in models or controllers
- Handle database sessions in logic layer with proper rollback

### Database Session Management
```python
# ✅ CORRECT - Handle sessions in logic layer
class UserLogic:
    @staticmethod
    def create_user(data):
        try:
            user = User(**data)
            db.session.add(user)
            db.session.commit()
            return user
        except Exception as e:
            db.session.rollback()
            raise BusinessError(f"Failed to create user: {str(e)}")
```

## Code Organization and Structure

### File Organization
```python
# src/models/user.py - ONLY database schema
# src/logic/user_logic.py - ALL business logic
# src/controllers/routes.py - ONLY request/response handling
```

### Import Standards
```python
# ✅ CORRECT - Clear, organized imports
# Standard library
import os
import json
from datetime import datetime

# Third-party
from flask import Flask, request, jsonify
from sqlalchemy import func

# Local application
from src.models.user import User
from src.logic.user_logic import UserLogic
from src.utils.validators import EmailValidator

# ❌ INCORRECT - Circular imports between layers
# Don't import controllers in logic layer
# Don't import logic in models
```

## Error Handling and Validation

### Exception Hierarchy
```python
# src/utils/exceptions.py
class AppError(Exception):
    """Base application exception"""
    pass

class ValidationError(AppError):
    """Data validation errors"""
    pass

class BusinessError(AppError):
    """Business rule violations"""
    pass

class NotFoundError(AppError):
    """Resource not found"""
    pass
```

### Validation in Logic Layer
- All input validation in logic layer, not controllers
- Use custom exceptions for different error types
- Controllers handle exceptions and return appropriate HTTP responses

### Error Handling in Controllers
```python
# ✅ CORRECT - Error handling in controllers
@app.route('/users', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        user = UserLogic.create_user(data)
        return jsonify(user.to_dict()), 201
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except BusinessError as e:
        return jsonify({'error': str(e)}), 409
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
```

## Testing Guidelines

### Unit Testing Logic Layer
- Focus tests on logic layer where business logic resides
- Test models for basic schema/serialization only
- Test controllers for HTTP response handling only

### Integration Testing Controllers
- Test complete request/response flows
- Verify proper error response codes
- Use test client for endpoint testing

## Performance and Development Guidelines

### Lean Code Principles
- Prefer simple, readable solutions over complex abstractions
- Avoid over-engineering for simple operations
- Only add dependencies when essential benefit is clear

### Configuration and Environment
```python
# config.py
import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'

class ProductionConfig(Config):
    DEBUG = False
    # Production database URL from environment
```

## Code Style and Formatting

### PEP 8 Compliance
- Use 4 spaces for indentation
- Line length maximum 88 characters (Black formatter standard)
- Use snake_case for functions and variables
- Use PascalCase for classes
- Use UPPER_CASE for constants

### Security Considerations
- Always validate input in logic layer
- Use SQLAlchemy ORM (prevents SQL injection)
- Sanitize user input before processing
- No raw SQL queries

These instructions ensure all Python code follows the constitutional principles of thin controllers, thin models, thick logic, and maintains the high-quality, lean development approach specified in the project constitution.