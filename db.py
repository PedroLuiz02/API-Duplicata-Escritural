import sqlite3

conexao = sqlite3.connect('banco.db', check_same_thread=False)
cursor = conexao.cursor()

cursor.execute("PRAGMA foreign_keys = ON;")

# Criar tabelas
cursor.execute("""CREATE TABLE IF NOT EXISTS sacador (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               nome TEXT NOT NULL,
               cnpj TEXT
)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS sacado (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               nome TEXT NOT NULL,
               cnpj TEXT
)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS duplicata (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               valor REAL NOT NULL,
               prazo TEXT NOT NULL,
               data TEXT NOT NULL,
               status TEXT DEFAULT 'emitida',
               sacador_id INTEGER,
               sacado_id INTEGER,
               FOREIGN KEY (sacador_id) REFERENCES sacador(id),
               FOREIGN KEY (sacado_id) REFERENCES sacado(id)
)""")

cursor.execute("SELECT COUNT(*) FROM duplicata")
total = cursor.fetchone()[0]

if total == 0:
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='duplicata'")
    
    cursor.execute("""
        INSERT OR IGNORE INTO sqlite_sequence (name, seq) 
        VALUES ('duplicata', 0)
    """)
    print("Auto increment resetado - começará do ID 1")
    
else:
    print(f"Tabela tem {total} registros - auto increment mantido")

conexao.commit()