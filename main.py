from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import csv
import os
import pytesseract
from PIL import Image
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# Caminhos dos arquivos
CAMINHO_USUARIOS = "usuarios.json"
CAMINHO_ACERVO = "acervo.csv"
CAMINHO_EMPRESTIMOS = "emprestimos.csv"
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ==== LOGIN ====
@app.route("/login", methods=["POST"])
def login():
    dados = request.get_json()
    usuario = dados.get("usuario")
    senha = dados.get("senha")
    try:
        with open(CAMINHO_USUARIOS, "r", encoding="utf-8") as f:
            usuarios = json.load(f)
    except:
        return jsonify({"erro": "Falha ao ler usuários"}), 500

    for u in usuarios:
        if u["usuario"] == usuario and u["senha"] == senha:
            return jsonify({"mensagem": "Login bem-sucedido", "tipo": u["tipo"]})
    return jsonify({"erro": "Usuário ou senha incorretos"}), 401

# ==== CADASTRO DE NOVO USUÁRIO ====
@app.route("/cadastrar", methods=["POST"])
def cadastrar_usuario():
    novo = request.get_json()
    try:
        with open(CAMINHO_USUARIOS, "r", encoding="utf-8") as f:
            usuarios = json.load(f)
    except:
        usuarios = []

    for u in usuarios:
        if u["usuario"] == novo["usuario"]:
            return jsonify({"erro": "Usuário já existe"}), 400

    usuarios.append(novo)
    with open(CAMINHO_USUARIOS, "w", encoding="utf-8") as f:
        json.dump(usuarios, f, indent=2, ensure_ascii=False)
    return jsonify({"mensagem": "Usuário cadastrado com sucesso!"})

# ==== VER ACERVO ====
@app.route("/acervo", methods=["GET"])
def ver_acervo():
    livros = []
    try:
        with open(CAMINHO_ACERVO, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            livros = list(reader)
    except FileNotFoundError:
        pass
    return jsonify(livros)

# ==== CADASTRAR LIVRO (normal) ====
@app.route("/acervo", methods=["POST"])
def cadastrar_livro():
    novo = request.get_json()
    campos = ["titulo", "autor"]
    livro = {campo: novo.get(campo, "") for campo in campos}
    try:
        existe = os.path.exists(CAMINHO_ACERVO)
        with open(CAMINHO_ACERVO, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=campos)
            if not existe:
                writer.writeheader()
            writer.writerow(livro)
        return jsonify({"mensagem": "Livro cadastrado com sucesso!"})
    except:
        return jsonify({"erro": "Erro ao salvar livro"}), 500

# ==== CADASTRAR LIVRO COM OCR ====
@app.route("/acervo/ocr", methods=["POST"])
def cadastrar_livro_com_ocr():
    if 'imagem' not in request.files:
        return jsonify({"erro": "Imagem não enviada"}), 400

    imagem = request.files['imagem']
    nome_arquivo = secure_filename(imagem.filename)
    caminho = os.path.join(UPLOAD_FOLDER, nome_arquivo)
    imagem.save(caminho)

    try:
        texto = pytesseract.image_to_string(Image.open(caminho))
        linhas = texto.split("\n")
        titulo = linhas[0] if linhas else ""
        autor = linhas[1] if len(linhas) > 1 else ""

        return cadastrar_livro_ocr_backend(titulo.strip(), autor.strip())
    except Exception as e:
        return jsonify({"erro": f"Erro no OCR: {str(e)}"}), 500

def cadastrar_livro_ocr_backend(titulo, autor):
    try:
        existe = os.path.exists(CAMINHO_ACERVO)
        with open(CAMINHO_ACERVO, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["titulo", "autor"])
            if not existe:
                writer.writeheader()
            writer.writerow({"titulo": titulo, "autor": autor})
        return jsonify({"mensagem": "Livro cadastrado por OCR com sucesso!"})
    except:
        return jsonify({"erro": "Erro ao salvar livro OCR"}), 500

# ==== REGISTRAR EMPRÉSTIMO ====
@app.route("/emprestimos", methods=["POST"])
def registrar_emprestimo():
    dados = request.get_json()
    campos = ["usuario", "titulo", "data"]
    emprestimo = {campo: dados.get(campo, "") for campo in campos}
    try:
        existe = os.path.exists(CAMINHO_EMPRESTIMOS)
        with open(CAMINHO_EMPRESTIMOS, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=campos)
            if not existe:
                writer.writeheader()
            writer.writerow(emprestimo)
        return jsonify({"mensagem": "Empréstimo registrado!"})
    except:
        return jsonify({"erro": "Erro ao registrar empréstimo"}), 500

# ==== VER EMPRÉSTIMOS ====
@app.route("/emprestimos", methods=["GET"])
def ver_emprestimos():
    try:
        with open(CAMINHO_EMPRESTIMOS, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return jsonify(list(reader))
    except:
        return jsonify([])

# ==== SAUDACAO ====
@app.route("/")
def inicio():
    return "✅ Backend da Estante Mágica está funcionando!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
