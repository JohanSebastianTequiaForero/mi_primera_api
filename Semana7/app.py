import sqlite3

def insertar_hotel(nombre, prefijo):
    conn = sqlite3.connect("hotels.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO hotels (name, prefix) VALUES (?, ?)", (nombre, prefijo))
    conn.commit()
    conn.close()
    print(f"🏨 Hotel '{nombre}' registrado con éxito")

def insertar_huesped(nombre, hotel_id, rol, tipo):
    conn = sqlite3.connect("hotels.db")
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO guests (full_name, hotel_id, role, tipo)
        VALUES (?, ?, ?, ?)
    """, (nombre, hotel_id, rol, tipo))
    conn.commit()
    conn.close()
    print(f"👤 Huésped '{nombre}' registrado en hotel {hotel_id}")

def listar_huespedes():
    conn = sqlite3.connect("hotels.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT g.full_name, h.name, g.role, g.tipo, g.created_at
        FROM guests g
        JOIN hotels h ON g.hotel_id = h.id
    """)
    registros = cur.fetchall()
    conn.close()

    print("\n📋 Lista de huéspedes:")
    for row in registros:
        print(f" - {row[0]} | Hotel: {row[1]} | Rol: {row[2]} | Tipo: {row[3]} | Fecha: {row[4]}")

if __name__ == "__main__":
    # Ejemplo de uso
    insertar_hotel("Hotel Central", "HC")
    insertar_hotel("Hotel Playa", "HP")

    insertar_huesped("Juan Pérez", 1, "Cliente", "A")
    insertar_huesped("Ana Gómez", 2, "Empleado", "B")

    listar_huespedes()
