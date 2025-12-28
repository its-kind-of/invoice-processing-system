import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path("data/invoices.db")

def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               invoice_number TEXT, 
               invoice_date TEXT,
               total_amount REAL, 
               source TEXT,
               raw_text TEXT,
               created_at TEXT
               )
               """)
    
    conn.commit()
    conn.close()

def insert_invoice(invoice: dict, raw_text: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO invoices (
                invoice_number, 
                invoice_date, 
                total_amount,
                source,
                raw_text,
                created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    invoice['invoice_number'],
                    invoice['invoice_date'],
                    invoice['total_amount'],
                    invoice['source'],
                    raw_text, 
                    datetime.utcnow().isoformat()
                ))
    
    conn.commit()
    conn.close()

