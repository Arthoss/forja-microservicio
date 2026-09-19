import os
import random
import psycopg2
import psycopg2.extras
from flask import Flask, jsonify

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")

def obtener_conexion():
    return psycopg2.connect(DATABASE_URL)

@app.route("/")
def home():
    return jsonify({"status": "ok", "servicio": "forja-microservicio-tips"})

@app.route("/api/tip")
def tip_aleatorio():
    conexion = obtener_conexion()
    cursor = conexion.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT texto, categoria FROM tips;")
    tips = cursor.fetchall()
    cursor.close()
    conexion.close()

    if not tips:
        return jsonify({"error": "No hay tips disponibles"}), 404

    return jsonify(dict(random.choice(tips)))

if __name__ == "__main__":
    app.run(debug=True)