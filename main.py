from flask import Flask, request, jsonify
import json

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Backend da Estante Mágica está funcionando!"

@app.route("/login", methods=["POST"])
def login():
    dados = request.json
    usuario = dados.get("usuario")
    senha = dados.get("senha")
    tipo = dados.get("tipo")

    with open("usuarios.json", "r", encoding="utf-8") as f:
        lista = json.load(f)

    for u in lista:
        if u["usuario"] == usuario and u["senha"] == senha and u["tipo"] == tipo:
            return jsonify({"mensagem": "Login realizado com sucesso!", "usuario": usuario})

    return jsonify({"erro": "Credenciais inválidas"}), 401

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
