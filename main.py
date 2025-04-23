from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)  # Permite requisições de qualquer origem (React incluso)

# Caminho do arquivo
CAMINHO_ARQUIVO = os.path.join(os.path.dirname(__file__), "usuarios.json")

# Carrega os usuários do arquivo JSON
def carregar_usuarios():
    try:
        with open(CAMINHO_ARQUIVO, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Salva os usuários no JSON
def salvar_usuarios(lista):
    with open(CAMINHO_ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(lista, f, indent=2, ensure_ascii=False)

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

@app.route("/cadastrar", methods=["POST"])
def cadastrar():
    dados = request.get_json()
    usuario = dados.get("usuario")
    senha = dados.get("senha")
    tipo = dados.get("tipo")

    if not usuario or not senha or not tipo:
        return jsonify({"erro": "Todos os campos são obrigatórios."}), 400

    usuarios = carregar_usuarios()
    if any(u["usuario"] == usuario for u in usuarios):
        return jsonify({"erro": "Usuário já existe."}), 409

    novo = {"usuario": usuario, "senha": senha, "tipo": tipo}
    usuarios.append(novo)
    salvar_usuarios(usuarios)

    return jsonify({"mensagem": "Usuário cadastrado com sucesso!"}), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
