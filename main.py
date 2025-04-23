
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import csv
import pytesseract
from PIL import Image
import base64
import io
import os

app = Flask(__name__)
CORS(app)

# Arquivos principais
ARQUIVO_USUARIOS = "usuarios.json"
ARQUIVO_ACERVO = "acervo.csv"

# === Funções auxiliares ===

def carregar_usuarios():
    try:
        with open(ARQUIVO_USUARIOS, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def salvar_livro(titulo, autor, genero):
    novo = [titulo, autor, genero]
    existe = False

    if not os.path.exists(ARQUIVO_ACERVO):
        with open(ARQUIVO_ACERVO, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Título", "Autor", "Gênero"])

    with open(ARQUIVO_ACERVO, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for linha in reader:
            if linha == novo:
                existe = True
                break

    if not existe:
        with open(ARQUIVO_ACERVO, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(novo)
        return True
    return False

def carregar_acervo():
    livros = []
    if os.path.exists(ARQUIVO_ACERVO):
        with open(ARQUIVO_ACERVO, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)
            for linha in reader:
                if len(linha) == 3:
                    livros.append({"titulo": linha[0], "autor": linha[1], "genero": linha[2]})
    return livros

# === Rotas ===

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

@app.route("/livros", methods=["GET"])
def listar_livros():
    return jsonify(carregar_acervo())

@app.route("/livros", methods=["POST"])
def cadastrar_livro():
    dados = request.json if request.is_json else request.form
    titulo = dados.get("titulo", "").strip()
    autor = dados.get("autor", "").strip()
    genero = dados.get("genero", "").strip()

    if not titulo or not autor or not genero:
        return jsonify({"erro": "Todos os campos são obrigatórios."}), 400

    if salvar_livro(titulo, autor, genero):
        return jsonify({"mensagem": "Livro cadastrado com sucesso!"})
    else:
        return jsonify({"erro": "Este livro já está cadastrado."}), 409

@app.route("/livros/ocr", methods=["POST"])
def cadastrar_livro_ocr():
    imagem_b64 = request.json.get("imagem_base64")
    if not imagem_b64:
        return jsonify({"erro": "Imagem não recebida."}), 400

    try:
        imagem_bytes = base64.b64decode(imagem_b64.split(",")[-1])
        imagem = Image.open(io.BytesIO(imagem_bytes))
        texto = pytesseract.image_to_string(imagem)

        linhas = texto.split("\n")
        titulo = linhas[0].strip() if len(linhas) > 0 else "Título Desconhecido"
        autor = linhas[1].strip() if len(linhas) > 1 else "Autor Desconhecido"
        genero = "Literatura"

        if salvar_livro(titulo, autor, genero):
            return jsonify({"mensagem": "Livro cadastrado via OCR!", "titulo": titulo, "autor": autor})
        else:
            return jsonify({"erro": "Este livro já está no acervo."}), 409
    except Exception as e:
        return jsonify({"erro": f"Erro ao processar a imagem: {str(e)}"}), 500

# === Execução ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
