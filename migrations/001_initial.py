def up(db):
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            system_name TEXT NOT NULL)
    """)


def down(db):
    db.execute("""
        DROP TABLE IF EXISTS users
    """)
