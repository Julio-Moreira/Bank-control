import sqlite3
from pathlib import Path

class DatabaseManager():
    DB_FILE = Path("bank_control.db") 

    def __init__(self):
        if self.DB_FILE.is_file():
            self.conn = sqlite3.connect(self.DB_FILE)
            self.cursor = self.conn.cursor()
            return
        
        self.conn = sqlite3.connect(self.DB_FILE)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Account (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Bank SMALLINT NOT NULL,
                Agency TINYINT NOT NULL,
                Name VARCHAR(30) NOT NULL,
                BalanceIntPart BIGINT NOT NULL,
                BalanceDecimalPart TINYINT NOT NULL,
                LastMovDay TINYINT NOT NULL,
                LastMovMounth TINYINT NOT NULL,
                LastMovYear TINYINT NOT NULL
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Launch (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Number BIGINT NOT NULL,
                Typ VARCHAR(2) NOT NULL,
                ValueIntPart BIGINT NOT NULL,
                Bank SMALLINT NOT NULL,
                Agency TINYINT NOT NULL,
                ValueDecimalPart TINYINT NOT NULL,
                History VARCHAR(30) NOT NULL,
                Situation TINYINT NOT NULL,
                IsChecked TINYINT NOT NULL,
                MovimentDay TINYINT NOT NULL,
                MovimentMonth TINYINT NOT NULL,
                MovimentYear TINYINT NOT NULL,
                EmissionDay TINYINT NOT NULL,
                EmissionMonth TINYINT NOT NULL,
                EmissionYear TINYINT NOT NULL
            );
        """)

        self.conn.commit()
                # FOREIGN KEY (Bank) REFERENCES Account(Bank)
    
    def execute(self, query, params=None):
        print(query,params)
        if params is None:
            params = []
        self.cursor.execute(query, params)
        self.conn.commit()

    def fetchall(self, query, params=None):
        if params is None:
            params = []
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def close(self):
        """Fecha a conexão com o banco."""
        self.conn.close()

if __name__ == "__main__":
    db = DatabaseManager()
    db.close()
