import sqlite3

def init_db():
    # Conectamos (si no existe hotels.db, lo crea)
    conn = sqlite3.connect("hotels.db")
    cur = conn.cursor()

    # Leemos el archivo models.sql
    with open("models.sql", "r", encoding="utf-8") as f:
        schema = f.read()

    # Ejecutamos el SQL
    cur.executescript(schema)
    conn.commit()
    conn.close()
    print("✅ Base de datos hotels.db creada con éxito")

if __name__ == "__main__":
    init_db()
