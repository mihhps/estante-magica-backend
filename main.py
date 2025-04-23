from flask import Flask, request, jsonify
from flask_cors import CORS
import csv
import os
import pytesseract
from PIL import Image

app = Flask(__name__)
CORS(app)

ACERVO_FILE = "acervo.csv"

# === Utilitários ===
def ler_acervo():
    livros = []
    if os.path.exists(ACERVO_FILE):
        with open(ACERVO_FILE, newline='', encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                livros.append(row)
    return livros

def salvar_acervo(livros):
    with open(ACERVO_FILE, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Título", "Autor", "Gênero"])
        writer.writeheader()
        writer.writerows(livros)

# === Rotas ===
@app.route("/")
def inicio():
    return "✅ Backend da Estante Mágica com acervo online e OCR!"

@app.route("/acervo", methods=["GET"])
def ver_acervo():
    return jsonify(ler_acervo())

@app.route("/acervo", methods=["POST"])
def adicionar_livro():
    novo = request.get_json()
    livros = ler_acervo()
    livros.append(novo)
    salvar_acervo(livros)
    return jsonify({"mensagem": "Livro adicionado com sucesso!"})

@app.route("/acervo/<titulo>", methods=["PUT"])
def editar_livro(titulo):
    dados = request.get_json()
    livros = ler_acervo()
    for livro in livros:
        if livro["Título"].lower() == titulo.lower():
            livro.update(dados)
            salvar_acervo(livros)
            return jsonify({"mensagem": "Livro atualizado!"})
    return jsonify({"erro": "Livro não encontrado"}), 404

@app.route("/acervo/<titulo>", methods=["DELETE"])
def excluir_livro(titulo):
    livros = ler_acervo()
    novos = [livro for livro in livros if livro["Título"].lower() != titulo.lower()]
    if len(novos) == len(livros):
        return jsonify({"erro": "Livro não encontrado"}), 404
    salvar_acervo(novos)
    return jsonify({"mensagem": "Livro excluído!"})

@app.route("/ocr", methods=["POST"])
def extrair_dados_ocr():
    if 'imagem' not in request.files:
        return jsonify({"erro": "Arquivo de imagem não enviado"}), 400

    imagem = request.files['imagem']
    imagem_salva = "temp_ocr.jpg"
    imagem.save(imagem_salva)

    try:
        texto = pytesseract.image_to_string(Image.open(imagem_salva), lang='por')
        linhas = texto.split("\n")
        titulo = linhas[0].strip() if len(linhas) > 0 else ""
        autor = linhas[1].strip() if len(linhas) > 1 else ""
        return jsonify({"titulo": titulo, "autor": autor})
    except Exception as e:
        return jsonify({"erro": f"Erro ao processar OCR: {str(e)}"}), 500
    finally:
        if os.path.exists(imagem_salva):
            os.remove(imagem_salva)

# === Rodar o servidor ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
