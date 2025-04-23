from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import csv
import os
import pytesseract
import base64
from PIL import Image
from io import BytesIO

app = Flask(__name__)
CORS(app)

# Caminho do arquivo de acervo
ARQUIVO_ACERVO = "acervo.csv"
ARQUIVO_USUARIOS = "usuarios.json"

# === Funções utilitárias ===
def carregar_usuarios():
    try:
        with open(ARQUIVO_USUARIOS, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def salvar_livro(titulo, autor, genero):
    novo = [titulo, autor, genero]
    if not os.path.exists(ARQUIVO_ACERVO):
        with open(ARQUIVO_ACERVO, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Titulo", "Autor", "Genero"])
            writer.writerow(novo)
    else:
        with open(ARQUIVO_ACERVO, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(novo)

def ler_acervo():
    livros = []
    if not os.path.exists(ARQUIVO_ACERVO):
        return livros
    with open(ARQUIVO_ACERVO, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for linha in reader:
            livros.append(linha)
    return livros

# === Rotas ===
@app.route("/")
def inicio():
    return "\u2705 Backend da Estante M\u00e1gica est\u00e1 online!"

@app.route("/login", methods=["POST"])
def login():
    dados = request.get_json()
    usuario = dados.get("usuario")
    senha = dados.get("senha")

    for u in carregar_usuarios():
        if u["usuario"] == usuario and u["senha"] == senha:
            return jsonify({"mensagem": "Login OK", "tipo": u["tipo"]})
    return jsonify({"erro": "Usu\u00e1rio ou senha incorretos"}), 401

@app.route("/acervo", methods=["GET"])
def listar_acervo():
    return jsonify(ler_acervo())

@app.route("/acervo", methods=["POST"])
def cadastrar_livro():
    dados = request.get_json()
    salvar_livro(dados["titulo"], dados["autor"], dados["genero"])
    return jsonify({"mensagem": "Livro cadastrado com sucesso!"})

@app.route("/ocr", methods=["POST"])
def extrair_texto_ocr():
    dados = request.get_json()
    imagem_base64 = dados.get("imagem")
    if not imagem_base64:
        return jsonify({"erro": "Imagem n\u00e3o enviada"}), 400

    try:
        imagem_bytes = base64.b64decode(imagem_base64)
        imagem = Image.open(BytesIO(imagem_bytes))
        texto = pytesseract.image_to_string(imagem, lang="por")
        linhas = [linha.strip() for linha in texto.split("\n") if linha.strip()]
        titulo = linhas[0] if len(linhas) > 0 else ""
        autor = linhas[1] if len(linhas) > 1 else ""
        return jsonify({"titulo": titulo, "autor": autor})
    except Exception as e:
        return jsonify({"erro": f"Erro ao processar imagem: {e}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
