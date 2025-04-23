from flask import Flask, request, jsonify
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)  # Permite requisições de qualquer origem (frontend React incluso)

# Carrega os usuários do arquivo JSON
def carregar_usuarios():
    try:
        with open("src/usuarios.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

@app.route("/")
def inicio():
    return "✅ Backend da Estante Mágica está funcionando!"

@app.route("/login", methods=["POST"])
def login():
    dados = request.get_json()
    usuario = dados.get("usuario")
    senha = dados.get("senha")

    usuarios = carregar_usuarios()
    for u in usuarios:
        if u["usuario"] == usuario and u["senha"] == senha:
            return jsonify({"mensagem": "Login bem-sucedido", "tipo": u["tipo"]})

    return jsonify({"erro": "Usuário ou senha incorretos"}), 401

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
