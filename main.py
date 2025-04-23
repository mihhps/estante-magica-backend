from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Arquivos
USUARIOS = "usuarios.json"
ACERVO = "acervo.json"
EMPRESTIMOS = "emprestimos.json"

def carregar_json(caminho):
    if not os.path.exists(caminho):
        return []
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_json(caminho, dados):
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

@app.route("/")
def inicio():
    return "✅ Backend Estante Mágica Online!"

@app.route("/login", methods=["POST"])
def login():
    dados = request.get_json()
    usuario = dados.get("usuario")
    senha = dados.get("senha")

    for u in carregar_json(USUARIOS):
        if u["usuario"] == usuario and u["senha"] == senha:
            return jsonify({"mensagem": "Login OK", "tipo": u["tipo"]})
    return jsonify({"erro": "Usuário ou senha incorretos"}), 401

@app.route("/acervo", methods=["GET"])
def ver_acervo():
    return jsonify(carregar_json(ACERVO))

@app.route("/acervo", methods=["POST"])
def cadastrar_livro():
    dados = request.get_json()
    titulo = dados.get("titulo")
    autor = dados.get("autor")
    genero = dados.get("genero")
    capa = dados.get("capa", "")

    if not titulo or not autor or not genero:
        return jsonify({"erro": "Dados incompletos"}), 400

    acervo = carregar_json(ACERVO)
    novo = {
        "id": len(acervo) + 1,
        "titulo": titulo,
        "autor": autor,
        "genero": genero,
        "capa": capa
    }
    acervo.append(novo)
    salvar_json(ACERVO, acervo)
    return jsonify({"mensagem": "Livro cadastrado com sucesso"})

@app.route("/emprestimos", methods=["GET"])
def ver_emprestimos():
    return jsonify(carregar_json(EMPRESTIMOS))

@app.route("/emprestimos", methods=["POST"])
def registrar_emprestimo():
    dados = request.get_json()
    aluno = dados.get("aluno")
    livro = dados.get("livro")
    data = datetime.now().strftime("%d/%m/%Y")

    if not aluno or not livro:
        return jsonify({"erro": "Campos obrigatórios faltando"}), 400

    emprestimos = carregar_json(EMPRESTIMOS)
    emprestimos.append({
        "aluno": aluno,
        "livro": livro,
        "data": data
    })
    salvar_json(EMPRESTIMOS, emprestimos)
    return jsonify({"mensagem": "Empréstimo registrado com sucesso"})

@app.route("/ocr", methods=["POST"])
def ocr_simulado():
    # Apenas simula leitura de imagem (OCR)
    return jsonify({
        "titulo": "Livro Detectado",
        "autor": "Autor Detectado"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
