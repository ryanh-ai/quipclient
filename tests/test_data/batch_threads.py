"""Test data for batch thread operations"""

# Simple threads test case
SIMPLE_THREADS = {
    "THREAD1": {"thread": {"id": "THREAD1", "title": "Thread 1", "type": "document"}},
    "THREAD2": {"thread": {"id": "THREAD2", "title": "Thread 2", "type": "document"}}
}

# Empty threads test case
EMPTY_THREADS = {}

# Test cases mapping
BATCH_THREAD_TEST_CASES = [
    ("simple_threads", SIMPLE_THREADS),
    ("empty_threads", EMPTY_THREADS)
]
