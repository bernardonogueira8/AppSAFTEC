"""
Migration: create_relember_user
Created at: 2026-04-06T15:54:42.346085
"""


def up(db):
    db.execute("""
        CREATE TABLE IF NOT EXISTS sei_dma (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            system_name TEXT NOT NULL)
    """)
    pass


def down(db):
    db.execute("DROP TABLE sei_dma")
    pass
