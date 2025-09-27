from flask import Blueprint, request, jsonify
from db import get_db
import redis, time
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from prometheus_client import Counter, Histogram

# Redis cache
cache = redis.Redis(host="localhost", port=6379, decode_responses=True)

# Blueprint para organizar rutas
bp = Blueprint("routes", __name__)

# --- Rate limiting (Tipo B: 60 req / 15 min) ---
limiter = Limiter(get_remote_address, default_limits=["60 per 15 minutes"])

# --- Métricas Prometheus ---
REQUEST_COUNT = Counter("http_requests_total", "Total requests", ["method", "endpoint"])
REQUEST_LATENCY = Histogram("http_request_latency_seconds", "Latency", ["endpoint"])


@bp.route("/guests", methods=["POST"])
@limiter.limit("60 per 15 minutes")  # Tipo B
def create_guest():
    start_time = time.time()
    REQUEST_COUNT.labels(method="POST", endpoint="/guests").inc()

    data = request.json
    full_name = data.get("full_name")
    hotel_id = data.get("hotel_id")
    role = data.get("role")
    tipo = data.get("tipo")

    if not (full_name and hotel_id and role and tipo in ["A","B","C","D"]):
        return jsonify({"error": "Invalid payload"}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO guests (full_name, hotel_id, role, tipo) VALUES (?,?,?,?)",
                (full_name, hotel_id, role, tipo))
    conn.commit()
    guest_id = cur.lastrowid
    conn.close()

    REQUEST_LATENCY.labels(endpoint="/guests").observe(time.time() - start_time)
    return jsonify({"id": guest_id, "full_name": full_name, "hotel_id": hotel_id, "role": role, "tipo": tipo}), 201


@bp.route("/guests/<int:guest_id>", methods=["GET"])
def get_guest(guest_id):
    start_time = time.time()
    REQUEST_COUNT.labels(method="GET", endpoint="/guests/<id>").inc()

    cache_key = f"guest:{guest_id}"
    cached = cache.get(cache_key)
    if cached:
        return jsonify({"fromCache": True, "payload": eval(cached)})

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""SELECT g.id, g.full_name, g.role, g.tipo, h.name as hotel, h.prefix
                   FROM guests g
                   JOIN hotels h ON g.hotel_id = h.id
                   WHERE g.id = ?""", (guest_id,))
    row = cur.fetchone()
    conn.close()

    if row:
        payload = dict(row)
        cache.setex(cache_key, 60, str(payload))
        REQUEST_LATENCY.labels(endpoint="/guests/<id>").observe(time.time() - start_time)
        return jsonify({"fromCache": False, "payload": payload})
    else:
        return jsonify({"error": "Not found"}), 404
