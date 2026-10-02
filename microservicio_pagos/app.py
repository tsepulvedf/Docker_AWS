from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/health", methods=["GET"])
def health():
    """Permite comprobar que el microservicio vive sin exponer su puerto."""
    return jsonify({"servicio": "pagos_flask", "version": "v2", "estado": "ok"}), 200


# Aceptamos con y sin barra final: Flask las trata como rutas distintas
@app.route("/api/v2/comprar", methods=["POST"])
@app.route("/api/v2/comprar/", methods=["POST"])
def realizar_compra():
    # silent=True evita el 415 en HTML si falta el Content-Type;
    # el 'or {}' evita el 400 en HTML si el cuerpo viene vacío.
    data = request.get_json(silent=True) or {}

    producto_id = data.get("producto_id")
    cantidad = data.get("cantidad", 1)

    if not producto_id:
        return jsonify({"error": "Falta el ID del producto"}), 400

    return jsonify({
        "mensaje": "Compra procesada exitosamente por el Microservicio Flask (v2)",
        "producto_id": producto_id,
        "cantidad": cantidad,
        "status": "Aprobado",
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)