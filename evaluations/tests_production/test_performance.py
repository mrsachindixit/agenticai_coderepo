"""Tests for Module 4: Performance optimization patterns."""

import sys
import os
import functools
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

def test_lru_cache_improvement():
    """Test that LRU cache improves performance for repeated calls."""
    
    @functools.lru_cache(maxsize=128)
    def expensive_function(x):
        # Simulate expensive computation
        time.sleep(0.01)
        return x * 2
    
    # First call (cache miss)
    start = time.time()
    result1 = expensive_function(5)
    time1 = time.time() - start
    
    # Second call (cache hit)
    start = time.time()
    result2 = expensive_function(5)
    time2 = time.time() - start
    
    assert result1 == result2 == 10
    assert time2 < time1 / 10, "Cache hit should be significantly faster"

def test_cache_stats():
    """Test that cache statistics are available."""
    @functools.lru_cache(maxsize=128)
    def test_func(x):
        return x + 1
    
    test_func(1)
    test_func(1)
    test_func(2)
    
    # Check cache info
    info = test_func.cache_info()
    assert info.hits >= 1, "Should have at least one cache hit"
    assert info.misses >= 1, "Should have at least one cache miss"
