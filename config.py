#!/usr/bin/env python3
"""
Configuration file for Real-Time Clipboard Redactor
Customize PII detection and redaction settings
"""

# Clipboard monitoring settings
CLIPBOARD_POLL_INTERVAL = 0.1  # How often to check clipboard (seconds)
MAX_CLIPBOARD_SIZE = 10000     # Maximum clipboard content size to process (characters)

# Logging configuration
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_TO_FILE = True
LOG_FILE = "clipboard_redactor.log"

# PII Entity Types to Monitor
PII_ENTITIES = [
    "PERSON",           # Names and personal identifiers
    "EMAIL_ADDRESS",    # Email addresses
    "PHONE_NUMBER",     # Phone numbers
    "IP_ADDRESS",       # IP addresses
    "LOCATION",         # Geographic locations
    "DATE_TIME",        # Dates and times
    "CRYPTO",          # Cryptocurrency addresses
]

# Custom redaction patterns
REDACTION_PATTERNS = {
    "DEFAULT": "[REDACTED]",
    "PERSON": "[NAME_REDACTED]",
    "EMAIL_ADDRESS": "[EMAIL_REDACTED]",
    "PHONE_NUMBER": "[PHONE_REDACTED]",
    "IP_ADDRESS": "[IP_REDACTED]",
    "CRYPTO": "[CRYPTO_REDACTED]",
    "LOCATION": "[LOCATION_REDACTED]",
    "DATE_TIME": "[DATE_REDACTED]",
}

# Performance settings
PERFORMANCE_TARGET_MS = 200  # Target processing time in milliseconds
ENABLE_PERFORMANCE_MONITORING = True

# Security settings
ENABLE_CONTENT_HASHING = True  # Use hashing to detect clipboard changes
HASH_ALGORITHM = "md5"         # Hashing algorithm (md5, sha1, sha256)

# Presidio settings
PRESIDIO_CONFIDENCE_THRESHOLD = 0.5  # Minimum confidence for PII detection (0.0-1.0)
PRESIDIO_LANGUAGE = "en"             # Language for analysis

# Development settings
SAVE_REDACTION_EXAMPLES = False  # Save examples for testing/improvement
EXAMPLES_FILE = "redaction_examples.json"

# Validation function for configuration
def validate_config():
    """Validate configuration settings"""
    errors = []
    
    if CLIPBOARD_POLL_INTERVAL <= 0:
        errors.append("CLIPBOARD_POLL_INTERVAL must be positive")
    
    if MAX_CLIPBOARD_SIZE <= 0:
        errors.append("MAX_CLIPBOARD_SIZE must be positive")
    
    if LOG_LEVEL not in ["DEBUG", "INFO", "WARNING", "ERROR"]:
        errors.append("LOG_LEVEL must be one of: DEBUG, INFO, WARNING, ERROR")
    
    if not (0.0 <= PRESIDIO_CONFIDENCE_THRESHOLD <= 1.0):
        errors.append("PRESIDIO_CONFIDENCE_THRESHOLD must be between 0.0 and 1.0")
    
    if PERFORMANCE_TARGET_MS <= 0:
        errors.append("PERFORMANCE_TARGET_MS must be positive")
    
    if HASH_ALGORITHM not in ["md5", "sha1", "sha256"]:
        errors.append("HASH_ALGORITHM must be one of: md5, sha1, sha256")
    
    return errors

# Load configuration from environment variables (optional)
def load_from_env():
    """Load configuration from environment variables"""
    import os
    
    global CLIPBOARD_POLL_INTERVAL, LOG_LEVEL, PRESIDIO_CONFIDENCE_THRESHOLD
    
    # Override with environment variables if present
    if "CLIPRE_POLL_INTERVAL" in os.environ:
        try:
            CLIPBOARD_POLL_INTERVAL = float(os.environ["CLIPRE_POLL_INTERVAL"])
        except ValueError:
            pass
    
    if "CLIPRE_LOG_LEVEL" in os.environ:
        LOG_LEVEL = os.environ["CLIPRE_LOG_LEVEL"].upper()
    
    if "CLIPRE_CONFIDENCE_THRESHOLD" in os.environ:
        try:
            PRESIDIO_CONFIDENCE_THRESHOLD = float(os.environ["CLIPRE_CONFIDENCE_THRESHOLD"])
        except ValueError:
            pass

# Initialize configuration
if __name__ == "__main__":
    # Validate configuration when run directly
    load_from_env()
    errors = validate_config()
    
    if errors:
        print("Configuration errors found:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("Configuration is valid!")
        
    print(f"\nCurrent configuration:")
    print(f"  Poll interval: {CLIPBOARD_POLL_INTERVAL}s")
    print(f"  Log level: {LOG_LEVEL}")
    print(f"  Max clipboard size: {MAX_CLIPBOARD_SIZE} chars")
    print(f"  PII entities: {len(PII_ENTITIES)} types")
    print(f"  Confidence threshold: {PRESIDIO_CONFIDENCE_THRESHOLD}")
    print(f"  Performance target: {PERFORMANCE_TARGET_MS}ms") 