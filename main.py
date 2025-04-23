from flask import Flask, request, jsonify
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)  # permite requisições de outros domínios

@app.route("/")
def home():
    return "✅ Backend da Estante Mágica está funcionando!"

@app.route("/login", methods=["POST"])
def login():
    dados = request.get_json()
    usuario = dados.get("usuario")
    senha = dados.get("senha")

    with open("usuarios.json", "r", encoding="utf-8") as f:
        usuarios = json.load(f)

    for u in usuarios:
        if u["usuario"] == usuario and u["senha"] == senha:
            return jsonify({"tipo": u["tipo"]})

    return jsonify({"erro": "Usuário ou senha incorretos"}), 401

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
