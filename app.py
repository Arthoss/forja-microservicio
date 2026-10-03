import os
import random
import requests
import psycopg2
import psycopg2.extras
from flask import Flask, jsonify

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")
RESPALDO_URL = os.environ.get(
    "RESPALDO_URL", "https://forja-ms-actualizar.onrender.com/api/tip"
)

def obtener_conexion():
    return psycopg2.connect(DATABASE_URL, connect_timeout=5)

@app.route("/")
def home():
    return jsonify({"status": "ok", "servicio": "forja-microservicio-tips"})

@app.route("/api/tip")
def tip_aleatorio():
    try:
        conexion = obtener_conexion()
        try:
            cursor = conexion.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute("SELECT texto, categoria FROM tips;")
            tips = cursor.fetchall()
            cursor.close()
        finally:
            conexion.close()

        if not tips:
            return jsonify({"error": "No hay tips disponibles"}), 404

        return jsonify(dict(random.choice(tips)))

    except Exception:
        # Resiliencia: si falla la base, pedimos el tip al microservicio Ruby
        try:
            r = requests.get(RESPALDO_URL, timeout=60)
            r.raise_for_status()
            tip = r.json()
            tip["origen"] = "respaldo"
            return jsonify(tip)
        except Exception:
            return jsonify({"error": "Servicio no disponible"}), 503

if __name__ == "__main__":
    app.run(debug=True)