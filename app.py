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
@app.route("/openapi.json")
def openapi():
    return jsonify({
        "openapi": "3.0.0",
        "info": {"title": "FORJA Microservicio - Tips (Flask)", "version": "1.0.0"},
        "paths": {
            "/api/tip": {
                "get": {
                    "summary": "Devuelve un tip aleatorio (con respaldo si falla la base)",
                    "responses": {
                        "200": {"description": "Tip aleatorio"},
                        "404": {"description": "No hay tips disponibles"},
                        "503": {"description": "Servicio no disponible"}
                    }
                }
            }
        }
    })

@app.route("/api-docs")
def api_docs():
    html = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>FORJA - Tips (Flask)</title>
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
  <script>SwaggerUIBundle({ url: "/openapi.json", dom_id: "#swagger-ui" });</script>
</body>
</html>"""
    return html, 200, {"Content-Type": "text/html; charset=utf-8"}

if __name__ == "__main__":
    app.run(debug=True)