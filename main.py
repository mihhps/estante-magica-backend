@app.route("/acervo", methods=["GET"])
def listar_livros():
    try:
        with open("acervo.csv", "r", encoding="utf-8") as f:
            linhas = f.readlines()[1:]  # ignora cabeçalho
            livros = [linha.strip().split(",") for linha in linhas]
            return jsonify([
                {"titulo": l[0], "autor": l[1], "genero": l[2]} for l in livros if len(l) == 3
            ])
    except FileNotFoundError:
        return jsonify([])

@app.route("/acervo", methods=["POST"])
def adicionar_livro():
    dados = request.get_json()
    try:
        with open("acervo.csv", "a", encoding="utf-8") as f:
            f.write(f"{dados['titulo']},{dados['autor']},{dados['genero']}\n")
        return jsonify({"mensagem": "Livro adicionado com sucesso!"})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route("/acervo/<titulo>", methods=["DELETE"])
def deletar_livro(titulo):
    try:
        with open("acervo.csv", "r", encoding="utf-8") as f:
            linhas = f.readlines()
        with open("acervo.csv", "w", encoding="utf-8") as f:
            for linha in linhas:
                if not linha.startswith(titulo + ","):
                    f.write(linha)
        return jsonify({"mensagem": "Livro removido com sucesso!"})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
