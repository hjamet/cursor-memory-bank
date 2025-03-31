import pytest
from src.hello_world import get_hello

def test_get_hello():
    """Tests the get_hello function."""
    assert get_hello() == "Hello, World!" 