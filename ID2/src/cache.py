import os
import json
import time
import hashlib


class CacheManager:
    def __init__(self, cache_dir, ttl_minutes):
        self.cache_dir = cache_dir
        self.ttl_seconds = ttl_minutes * 60
        os.makedirs(cache_dir, exist_ok=True)

    def _path(self, key):
        h = hashlib.md5(key.encode('utf-8')).hexdigest()
        return os.path.join(self.cache_dir, f'{h}.json')

    def get(self, key):
        path = self._path(key)
        if not os.path.exists(path):
            return None
        if time.time() - os.path.getmtime(path) > self.ttl_seconds:
            return None
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save(self, key, rows):
        path = self._path(key)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(rows, f, ensure_ascii=False, indent=2)

    def save_text(self, key, text):
        path = self._path(key).replace('.json', '.html')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(text)