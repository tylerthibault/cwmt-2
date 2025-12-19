import secrets
import string

def generate_random_password(length=12):
    """
    Generate a secure random password.
    
    Args:
        length (int): Length of the password. Default is 12 characters.
        
    Returns:
        str: A random password containing uppercase, lowercase, digits, and special characters.
    """
    # Define character sets
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    special_chars = "!@#$%&*"
    
    # Combine all characters
    all_chars = lowercase + uppercase + digits + special_chars
    
    # Ensure the password contains at least one of each type
    password = [
        secrets.choice(lowercase),
        secrets.choice(uppercase),
        secrets.choice(digits),
        secrets.choice(special_chars)
    ]
    
    # Fill the rest of the password with random characters
    password += [secrets.choice(all_chars) for _ in range(length - 4)]
    
    # Shuffle the password to avoid predictable patterns
    secrets.SystemRandom().shuffle(password)
    
    return ''.join(password)


def generate_simple_password(length=8):
    """
    Generate a simpler random password (alphanumeric only).
    
    Args:
        length (int): Length of the password. Default is 8 characters.
        
    Returns:
        str: A random alphanumeric password.
    """
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))


def hash_string(incoming_string):
    """
        Hash a password using flask-bcrypt.
    """
    from flask_bcrypt import generate_password_hash
    print(f"Hashing string: {incoming_string}")
    hash = generate_password_hash(incoming_string).decode('utf-8')
    print(f"Generated hash: {hash}")
    return hash

def verify_hash(hashed_string, incoming_string):
    """
    Verify a password against a hashed password using flask-bcrypt.
    """
    from flask_bcrypt import check_password_hash
    print(f"Verifying hash: {hashed_string} with incoming string: {incoming_string}")
    return check_password_hash(hashed_string, incoming_string)