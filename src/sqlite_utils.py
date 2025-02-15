from contextlib import contextmanager
import time
@contextmanager
def sqlite_timelimit(conn, ms):
    deadline = time.perf_counter() + (ms / 1000)
    # n is the number of SQLite virtual machine instructions that will be
    # executed between each check. It takes about 0.08ms to execute 1000.
    # https://github.com/simonw/datasette/issues/1679
    n = 1000
    if ms <= 20:
        # This mainly happens while executing our test suite
        n = 1

    def handler():
        if time.perf_counter() >= deadline:
            # Returning 1 terminates the query with an error
            return 1

    conn.set_progress_handler(handler, n)
    try:
        yield
    finally:
        conn.set_progress_handler(None, n)