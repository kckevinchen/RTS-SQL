import sqlite3
from sqlite_utils import *
import numpy as np
class SQLRunner:
    def __init__(self, db_path: str,time_limit_ms=5000):
        """
        Initializes the SQLRunner with a database connection.
        
        :param db_path: Path to the SQLite database file.
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.time_limit_ms = time_limit_ms

    def run_query(self, sql_query: str):
        """
        Executes an SQL query on the database and optionally saves the result.
        
        :param sql_query: The SQL query to execute.
        :param save_path: Optional path to save the query results as a CSV file.
        :return: Query result as a Pandas DataFrame.
        """
        with sqlite_timelimit(self.conn, self.time_limit_ms):
            try:
                cursor = self.conn.cursor()
                cursor.execute(sql_query)
                result = np.array(cursor.fetchall())
            except Exception as error:
                return None, error
        return result, None
    