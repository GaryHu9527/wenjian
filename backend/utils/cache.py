import time

class MemoryCache:
    def __init__(self, ttl_seconds=1800):
        self.ttl_seconds = ttl_seconds
        self._items = {}

    def get(self, key):
        item = self._items.get(key)
        if not item or item[0] < time.monotonic():
            self._items.pop(key, None)
            return None
        return item[1]

    def set(self, key, value):
        self._items[key] = (time.monotonic() + self.ttl_seconds, value)
        return value
