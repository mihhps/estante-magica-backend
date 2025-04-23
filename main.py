
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "✅ Backend Estante Mágica ativo!"

@app.route("/login", methods=["POST"])
def login():
    try:
        with open("usuarios.json", "r", encoding="utf-8") as f:
            usuarios = json.load(f)
    except FileNotFoundError:
        return jsonify({"erro": "Base de usuários não encontrada"}), 500

    dados = request.get_json()
    for u in usuarios:
        if u["usuario"] == dados["usuario"] and u["senha"] == dados["senha"]:
            return jsonify({"tipo": u["tipo"]})
    return jsonify({"erro": "Usuário ou senha incorretos"}), 401

@app.route("/acervo", methods=["GET"])
def consultar_acervo():
    try:
        with open("acervo.json", "r", encoding="utf-8") as f:
            acervo = json.load(f)
        return jsonify(acervo)
    except FileNotFoundError:
        return jsonify([])

@app.route("/acervo", methods=["POST"])
def cadastrar_livro():
    novo = request.get_json()
    try:
        with open("acervo.json", "r", encoding="utf-8") as f:
            acervo = json.load(f)
    except FileNotFoundError:
        acervo = []

    acervo.append(novo)
    with open("acervo.json", "w", encoding="utf-8") as f:
        json.dump(acervo, f, indent=2, ensure_ascii=False)
    return jsonify({"mensagem": "Livro adicionado com sucesso!"})

@app.route("/acervo/<titulo>", methods=["PUT"])
def editar_livro(titulo):
    dados = request.get_json()
    try:
        with open("acervo.json", "r", encoding="utf-8") as f:
            acervo = json.load(f)
    except FileNotFoundError:
        return jsonify({"erro": "Arquivo de acervo não encontrado"}), 404

    for livro in acervo:
        if livro["titulo"] == titulo:
            livro.update(dados)
            break
    else:
        return jsonify({"erro": "Livro não encontrado"}), 404

    with open("acervo.json", "w", encoding="utf-8") as f:
        json.dump(acervo, f, indent=2, ensure_ascii=False)
    return jsonify({"mensagem": "Livro atualizado com sucesso!"})

@app.route("/acervo/<titulo>", methods=["DELETE"])
def deletar_livro(titulo):
    try:
        with open("acervo.json", "r", encoding="utf-8") as f:
            acervo = json.load(f)
    except FileNotFoundError:
        return jsonify({"erro": "Arquivo de acervo não encontrado"}), 404

    acervo = [livro for livro in acervo if livro["titulo"] != titulo]
    with open("acervo.json", "w", encoding="utf-8") as f:
        json.dump(acervo, f, indent=2, ensure_ascii=False)
    return jsonify({"mensagem": "Livro removido com sucesso!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
