from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import csv
import os
from werkzeug.utils import secure_filename
from PIL import Image
import pytesseract

app = Flask(__name__)
CORS(app)

USUARIOS_JSON = "usuarios.json"
ACERVO_CSV = "acervo.csv"
EMPRESTIMOS_CSV = "emprestimos.csv"

# ========== FUNÇÕES AUXILIARES ==========

def carregar_usuarios():
    if not os.path.exists(USUARIOS_JSON):
        return []
    with open(USUARIOS_JSON, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_usuarios(usuarios):
    with open(USUARIOS_JSON, "w", encoding="utf-8") as f:
        json.dump(usuarios, f, ensure_ascii=False, indent=2)

def carregar_acervo():
    livros = []
    if os.path.exists(ACERVO_CSV):
        with open(ACERVO_CSV, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                livros.append(row)
    return livros

def salvar_acervo(livros):
    with open(ACERVO_CSV, "w", newline="", encoding="utf-8") as f:
        campos = ["id", "titulo", "autor"]
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        for livro in livros:
            writer.writerow(livro)

# ========== ROTAS ==========

@app.route("/")
def inicio():
    return "✅ Backend da Estante Mágica está online!"

@app.route("/login", methods=["POST"])
def login():
    dados = request.get_json()
    usuarios = carregar_usuarios()
    for u in usuarios:
        if u["usuario"] == dados.get("usuario") and u["senha"] == dados.get("senha"):
            return jsonify({"mensagem": "Login bem-sucedido", "tipo": u["tipo"]})
    return jsonify({"erro": "Usuário ou senha incorretos"}), 401

@app.route("/cadastrar", methods=["POST"])
def cadastrar_usuario():
    novo = request.get_json()
    usuarios = carregar_usuarios()
    if any(u["usuario"] == novo["usuario"] for u in usuarios):
        return jsonify({"erro": "Usuário já existe"}), 400
    usuarios.append(novo)
    salvar_usuarios(usuarios)
    return jsonify({"mensagem": "Usuário cadastrado com sucesso!"})

@app.route("/acervo", methods=["GET", "POST", "PUT", "DELETE"])
def gerenciar_acervo():
    if request.method == "GET":
        return jsonify(carregar_acervo())
    
    elif request.method == "POST":
        novo = request.get_json()
        livros = carregar_acervo()
        novo["id"] = str(len(livros) + 1)
        livros.append(novo)
        salvar_acervo(livros)
        return jsonify({"mensagem": "Livro cadastrado com sucesso!"})

    elif request.method == "PUT":
        dados = request.get_json()
        livros = carregar_acervo()
        for livro in livros:
            if livro["id"] == dados["id"]:
                livro["titulo"] = dados["titulo"]
                livro["autor"] = dados["autor"]
        salvar_acervo(livros)
        return jsonify({"mensagem": "Livro atualizado com sucesso!"})

    elif request.method == "DELETE":
        id_livro = request.args.get("id")
        livros = carregar_acervo()
        livros = [livro for livro in livros if livro["id"] != id_livro]
        salvar_acervo(livros)
        return jsonify({"mensagem": "Livro deletado com sucesso!"})

@app.route("/ocr", methods=["POST"])
def extrair_dados_ocr():
    if "imagem" not in request.files:
        return jsonify({"erro": "Imagem não enviada."}), 400
    imagem = request.files["imagem"]
    nome_arquivo = secure_filename(imagem.filename)
    imagem.save(nome_arquivo)
    
    try:
        texto = pytesseract.image_to_string(Image.open(nome_arquivo), lang='por')
        linhas = texto.strip().split("\n")
        titulo = linhas[0] if linhas else "Título não identificado"
        autor = linhas[1] if len(linhas) > 1 else "Autor não identificado"
        os.remove(nome_arquivo)
        return jsonify({"titulo": titulo, "autor": autor})
    except Exception as e:
        return jsonify({"erro": f"OCR falhou: {str(e)}"}), 500

@app.route("/emprestimos", methods=["GET"])
def listar_emprestimos():
    emprestimos = []
    if os.path.exists(EMPRESTIMOS_CSV):
        with open(EMPRESTIMOS_CSV, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                emprestimos.append(row)
    return jsonify(emprestimos)

# ========== EXECUÇÃO LOCAL ==========
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
