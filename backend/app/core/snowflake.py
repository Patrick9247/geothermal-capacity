import threading
import time
class SnowflakeIdGenerator:
    
    EPOCH_MS = 1_704_067_200_000  # 2024-01-01T00:00:00Z
    WORKER_BITS = 10
    SEQUENCE_BITS = 12
    MAX_WORKER_ID = (1 << WORKER_BITS) - 1
    MAX_SEQUENCE = (1 << SEQUENCE_BITS) - 1
    WORKER_SHIFT = SEQUENCE_BITS
    TIMESTAMP_SHIFT = WORKER_BITS + SEQUENCE_BITS

    def __init__(self, worker_id: int):
        if not 0 <= worker_id <= self.MAX_WORKER_ID:
            raise ValueError(f"worker_id must be between 0 and {self.MAX_WORKER_ID}")
        self.worker_id = worker_id
        self._sequence = 0
        self._last_timestamp = -1
        self._lock = threading.Lock()

    def next_id(self) -> int:
        with self._lock:
            timestamp = self._timestamp_ms()
            if timestamp < self._last_timestamp:
                timestamp = self._last_timestamp
            if timestamp == self._last_timestamp:
                self._sequence = (self._sequence + 1) & self.MAX_SEQUENCE
                if self._sequence == 0:
                    timestamp = self._wait_next_millisecond(timestamp)
            else:
                self._sequence = 0
            self._last_timestamp = timestamp
            return ((timestamp - self.EPOCH_MS) << self.TIMESTAMP_SHIFT) | (self.worker_id << self.WORKER_SHIFT) | self._sequence

    @staticmethod
    def _timestamp_ms() -> int:
        return time.time_ns() // 1_000_000

    def _wait_next_millisecond(self, previous_timestamp: int) -> int:
        timestamp = self._timestamp_ms()
        while timestamp <= previous_timestamp:
            timestamp = self._timestamp_ms()
        return timestamp
