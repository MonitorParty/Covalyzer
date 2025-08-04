import sqlite3
import os
from typing import List, Tuple


class DatabaseConnector:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def fetch_testcases(self, offset: int, batch_size: int, only_queue=False) -> List[Tuple[int, bytes]]:
        if only_queue:
            self.cursor.execute("""SELECT testcases.id, testcases.value 
                                FROM testcases
                                JOIN queue ON testcases.id = queue.id 
                                LIMIT ? OFFSET ?""", (batch_size, offset))
        else: 
            self.cursor.execute("""SELECT id, value 
                                FROM testcases 
                                LIMIT ? OFFSET ?""", (batch_size, offset))

        return self.cursor.fetchall() 

    def fetch_queue_snapshots(self, snapshot_intervals=900) -> dict[int, List[Tuple[int, bytes]]]:
        """
        Return a dict mapping snapshot index to list of (id, value) testcases.
        Each snapshot contains queue entries added within a 15-minute window
        """
        self.cursor.execute("SELECT queue.id, queue.timestamp, testcases.value FROM queue JOIN testcases ON queue.id = testcases.id ORDER BY queue.timestamp ASC")
        rows = self.cursor.fetchall()

        snapshots = {}
        for tc_id, ts, value in rows:
            bucket = ts // snapshot_intervals 
            snapshots.setdefault(bucket, []).append((tc_id, value))

        return snapshots 

    def fetch_restarts(self) -> List[int]:
        self.cursor.execute("SELECT id, eventtype FROM restarts ORDER BY id ASC")
        return [row[0] for row in self.cursor.fetchall()]

    def close(self):
        self.conn.close()




