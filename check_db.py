import sqlite3

def check_database():
    conn = sqlite3.connect('jiraclone.db')
    c = conn.cursor()
    
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [table[0] for table in c.fetchall()]
    print("\nTables in database:", tables)
    for table in tables:
        c.execute(f"SELECT COUNT(*) FROM {table}")
        count = c.fetchone()[0]
        print(f"\n{table}: {count} records")
        
        if count > 0:
            c.execute(f"SELECT * FROM {table} LIMIT 1")
            columns = [description[0] for description in c.description]
            print("Columns:", columns)
            print("Sample row:", c.fetchone())

if __name__ == '__main__':
    check_database()
