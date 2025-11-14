import time

def retry_session(sessionmaker_fn, retries=5, delay=1):
    for attempt in range(retries):
        try:
            return sessionmaker_fn()
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(delay)
