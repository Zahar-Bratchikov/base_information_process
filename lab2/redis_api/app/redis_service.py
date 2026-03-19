from __future__ import annotations

from typing import Dict, List, Optional

import redis


class RedisService:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    @staticmethod
    def _decode(value: bytes | str | None) -> str | None:
        if value is None:
            return None
        if isinstance(value, bytes):
            return value.decode()
        return value

    def exists(self, key: str) -> bool:
        return bool(self.redis.exists(key))

    # -----------------------------
    # STRING / INTEGER
    # -----------------------------
    def set_string(self, key: str, value: str, ttl_seconds: int | None = None) -> None:
        if ttl_seconds is None:
            self.redis.set(key, value)
        else:
            self.redis.set(key, value, ex=ttl_seconds)

    def get_string(self, key: str) -> Optional[str]:
        value = self.redis.get(key)
        return self._decode(value)

    def delete_key(self, key: str) -> int:
        return int(self.redis.delete(key))

    def set_ttl(self, key: str, ttl_seconds: int) -> bool:
        return bool(int(self.redis.expire(key, ttl_seconds)))

    def incr_string(self, key: str, delta: int) -> int:
        return int(self.redis.incrby(key, delta))

    # Integer хранится как строка Redis, но интерпретируется как int.
    def set_integer(self, key: str, value: int, ttl_seconds: int | None = None) -> None:
        self.set_string(key, str(int(value)), ttl_seconds=ttl_seconds)

    def get_integer(self, key: str) -> Optional[int]:
        raw = self.get_string(key)
        if raw is None:
            return None
        try:
            return int(raw)
        except ValueError as e:
            raise ValueError(f"Value at key={key!r} is not an integer") from e

    def incr_integer(self, key: str, delta: int) -> int:
        return self.incr_string(key, delta)

    # -----------------------------
    # LIST
    # -----------------------------
    def list_replace(self, key: str, values: List[str], ttl_seconds: int | None = None) -> None:
        pipe = self.redis.pipeline()
        pipe.delete(key)
        if values:
            pipe.rpush(key, *values)
        pipe.execute()

        if ttl_seconds is not None:
            self.redis.expire(key, ttl_seconds)

    def list_get(self, key: str) -> List[str]:
        values = self.redis.lrange(key, 0, -1)
        return [self._decode(v) or "" for v in values]

    def list_increment_by_index(self, key: str, index: int, delta: int) -> int:
        # Atomic increment using Lua:
        # 1) read element
        # 2) validate it's an integer
        # 3) compute new value
        # 4) LSET back
        lua = """
        local val = redis.call('LINDEX', KEYS[1], tonumber(ARGV[1]))
        if not val then
          return {err='INDEX_OUT_OF_RANGE'}
        end
        val = tonumber(val)
        if not val then
          return {err='VALUE_NOT_INTEGER'}
        end
        local new_val = val + tonumber(ARGV[2])
        redis.call('LSET', KEYS[1], tonumber(ARGV[1]), new_val)
        return new_val
        """
        result = self.redis.eval(lua, 1, key, int(index), int(delta))
        return int(result)

    # -----------------------------
    # HASH
    # -----------------------------
    def hash_upsert(self, key: str, fields: Dict[str, str], ttl_seconds: int | None = None) -> None:
        # HMSET semantics: update only provided fields.
        if fields:
            self.redis.hset(key, mapping=fields)
        if ttl_seconds is not None:
            self.redis.expire(key, ttl_seconds)

    def hash_get_all(self, key: str) -> Dict[str, str]:
        raw = self.redis.hgetall(key)
        result: Dict[str, str] = {}
        for k, v in raw.items():
            kk = self._decode(k) or ""
            vv = self._decode(v) or ""
            result[kk] = vv
        return result

    def hash_increment_field(self, key: str, field: str, delta: int) -> int:
        return int(self.redis.hincrby(key, field, delta))

