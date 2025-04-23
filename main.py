from flask import request
import pytesseract
from PIL import Image
import io
import base64

app = Flask(__name__)
CORS(app)

ACERVO_PATH = "acervo.json"

# === Funções auxiliares ===
def carregar_acervo():
    if not os.path.exists(ACERVO_PATH):
        with open(ACERVO_PATH, "w", encoding="utf-8") as f:
            json.dump([], f)
    with open(ACERVO_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_acervo(lista):
    with open(ACERVO_PATH, "w", encoding="utf-8") as f:
        json.dump(lista, f, ensure_ascii=False, indent=4)

# === Rotas ===

@app.route("/")
def home():
    return "✅ Backend da Estante Mágica Online!"

# --- LOGIN ---
@app.route("/login", methods=["POST"])
def login():
    try:
        with open("usuarios.json", "r", encoding="utf-8") as f:
            usuarios = json.load(f)
    except FileNotFoundError:
        return jsonify({"erro": "Arquivo de usuários não encontrado"}), 500

    dados = request.get_json()
    usuario = dados.get("usuario")
    senha = dados.get("senha")

    for u in usuarios:
        if u["usuario"] == usuario and u["senha"] == senha:
            return jsonify({"mensagem": "Login bem-sucedido", "tipo": u["tipo"]})
    return jsonify({"erro": "Usuário ou senha incorretos"}), 401

# --- ACERVO ---
@app.route("/acervo", methods=["GET"])
def listar_acervo():
    return jsonify(carregar_acervo())

@app.route("/acervo", methods=["POST"])
def cadastrar_livro():
    dados = request.get_json()
    acervo = carregar_acervo()
    acervo.append(dados)
    salvar_acervo(acervo)
    return jsonify({"mensagem": "Livro cadastrado com sucesso!"}), 201

@app.route("/acervo/<int:index>", methods=["PUT"])
def editar_livro(index):
    acervo = carregar_acervo()
    if 0 <= index < len(acervo):
        acervo[index] = request.get_json()
        salvar_acervo(acervo)
        return jsonify({"mensagem": "Livro atualizado com sucesso!"})
    return jsonify({"erro": "Livro não encontrado"}), 404

@app.route("/acervo/<int:index>", methods=["DELETE"])
def deletar_livro(index):
    acervo = carregar_acervo()
    if 0 <= index < len(acervo):
        acervo.pop(index)
        salvar_acervo(acervo)
        return jsonify({"mensagem": "Livro removido com sucesso!"})
    return jsonify({"erro": "Livro não encontrado"}), 404

@app.route("/ocr", methods=["POST"])
def ocr_livro():
    try:
        dados = request.get_json()
        imagem_base64 = dados.get("imagem")

        if not imagem_base64:
            return jsonify({"erro": "Imagem não fornecida"}), 400

        imagem_bytes = base64.b64decode(imagem_base64)
        imagem = Image.open(io.BytesIO(imagem_bytes))

        texto = pytesseract.image_to_string(imagem)

        linhas = texto.split("\n")
        linhas = [linha.strip() for linha in linhas if linha.strip()]

        titulo = linhas[0] if len(linhas) > 0 else "Desconhecido"
        autor = linhas[1] if len(linhas) > 1 else "Desconhecido"

        return jsonify({"titulo": titulo, "autor": autor})

    except Exception as e:
        return jsonify({"erro": f"OCR falhou: {str(e)}"}), 500

# === Inicia servidor ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
