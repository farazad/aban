import random

def buy_from_exchange(symbol, amount):
    """Simulate exchange purchase; returns True if successful, False otherwise."""
    # Simulate API success/failure
    success = random.choice([True, False])
    return success