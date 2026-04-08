
def up(db):
    db.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')

def down(db):
    db.execute('''
        DROP TABLE IF EXISTS users
    ''')               
