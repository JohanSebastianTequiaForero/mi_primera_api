from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
DB_NAME = "hotels.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# Crear huésped
@app.route("/guests", methods=["POST"])
def create_guest():
    data = request.get_json()
    full_name = data.get("full_name")
    hotel_id = data.get("hotel_id")
    role = data.get("role")
    tipo = data.get("tipo")

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO guests (full_name, hotel_id, role, tipo) VALUES (?, ?, ?, ?)",
        (full_name, hotel_id, role, tipo),
    )
    conn.commit()
    guest_id = cur.lastrowid
    conn.close()

    return jsonify({"message": "Huésped creado", "id": guest_id}), 201

# Consultar huésped por ID
@app.route("/guests/<int:guest_id>", methods=["GET"])
def get_guest(guest_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT g.id, g.full_name, g.role, g.tipo, g.created_at, h.name as hotel
        FROM guests g
        JOIN hotels h ON g.hotel_id = h.id
        WHERE g.id = ?
        """,
        (guest_id,),
    )
    row = cur.fetchone()
    conn.close()

    if row is None:
        return jsonify({"error": "Huésped no encontrado"}), 404

    return jsonify(dict(row))

# Consultar todos los huéspedes
@app.route("/guests", methods=["GET"])
def list_guests():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT g.id, g.full_name, g.role, g.tipo, g.created_at, h.name as hotel
        FROM guests g
        JOIN hotels h ON g.hotel_id = h.id
        """
    )
    rows = cur.fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

if __name__ == "__main__":
    app.run(debug=True)
