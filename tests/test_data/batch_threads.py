"""Test data for batch thread operations"""

# Single thread test case
SINGLE_THREAD = {
    "THREAD1": {"thread": {"id": "THREAD1", "title": "Thread 1", "type": "document"}}
}

# Two threads test case
TWO_THREADS = {
    "THREAD1": {"thread": {"id": "THREAD1", "title": "Thread 1", "type": "document"}},
    "THREAD2": {"thread": {"id": "THREAD2", "title": "Thread 2", "type": "document"}}
}

# Twenty threads test case
TWENTY_THREADS = {
    f"THREAD{i}": {
        "thread": {
            "id": f"THREAD{i}",
            "title": f"Thread {i}",
            "type": "document"
        }
    } for i in range(1, 21)
}

# Empty threads test case
EMPTY_THREADS = {}

# Test cases mapping
BATCH_THREAD_TEST_CASES = [
    ("single_thread", SINGLE_THREAD),
    ("two_threads", TWO_THREADS),
    ("twenty_threads", TWENTY_THREADS),
    ("empty_threads", EMPTY_THREADS)
]
